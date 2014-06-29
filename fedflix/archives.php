<?php

/* Screen scraping for archives.gov
 *	Copyright and all that jazz.
 */

require('common.inc.php');
//$MTEMP->debugging=true;

//$CONFIG['apiUrl'] = 'http://en.wikipedia.org/w/api.php';

$curlObj = NULL;

ResetCurl();


if (!isset($_REQUEST['archiveHint']) 
	|| empty($_REQUEST['archiveHint']))
{
	$MTEMP->display('archives.t');
} else {
	$_REQUEST['archiveHint'] = (int) $_REQUEST['archiveHint'];
	DoIt();
}

//DoIt();

// yeah, because that o with a thing through it is retarded to have on enwiki. :P
function stupid_encode($stuff)
{

	$str = '';
	foreach ($stuff as $key=>$val)
	{
		$str .= "$key=" . utf8_encode($val) . "&";
	}
	$str = substr($str, 0, -1);

	return $str;

}


function niceify($stuff)
{
	$stuff = strip_tags($stuff);
	preg_replace('~[\t]~', ' ', $stuff);
	return trim($stuff);
}



function DoIt() {

	global $curlObj, $MTEMP;

	//http://arcweb.archives.gov/arc/action/ExternalIdSearch?id=306514

	
	$curlObj->url = "http://arcweb.archives.gov/arc/action/ExternalIdSearch?id={$_REQUEST['archiveHint']}";

	$res = $curlObj->DoCurl();

	$metaData=array();
	$meta=array();
	$meta['resURL'] = $curlObj->url;

	$n = preg_match('~<strong class="sFC">(.*)</strong>~isSU', $res, $m);
	//clean off redundant sfcextra tag that adds the date again.
	$firstPass = preg_replace('~<em class="sFCextra">.*</em>~isSU', '', $m[1]);
	$meta['descr'] = niceify($firstPass);

	//$n = preg_match('~<strong class="arcID">.*([\d]+)</strong>~isSU', $res, $m);
	//$meta['archID'] = niceify($m[1]);

        $n = preg_match('~Local Identifier ([^<]+)\<~isSU', $res, $m);
        $meta['localIdentifier'] = $m[1];

	$n = preg_match('~<span class="LOD">(.+)</span>~isSU', $res, $m);
	$firstPass = preg_replace('~Item from ~isSU', '', $m[1]);
	$meta['lod'] = niceify($firstPass);


        // crawl the stuff from the scope and content tab.
        $n = preg_match('~a href\="(/arc/action/ShowFullRecordLinked\?tab\=showFullDescriptionTabs/scope([^"]+))"\>~isSU', $res, $m);
	if ($n == 0)
	{
		$meta['scopeAndContent'] = '';
	} else {
	        $meta['linkToScope'] = 'http://arcweb.archives.gov' . $m[1];
	        $curlObj->url = $meta['linkToScope'];
	        $resScope = $curlObj->DoCurl();

		$n = preg_match('~\<div class="genPad"\>\s*\<pre\>(.*)\</pre\>\s*\</div\>~isSU', $resScope, $m);
		$meta['scopeAndContent'] = niceify($m[1]);
	}


        // crawl the remaining stuff from the hierarchy.
        $n = preg_match('~a href\="(/arc/action/ShowFullRecordLinked\?tab\=showFullDescriptionTabs/hierarchy([^"]+))"\>~isSU', $res, $m);
        $meta['linkToHierarchy'] = 'http://arcweb.archives.gov' . $m[1];
        $curlObj->url = $meta['linkToHierarchy'];
        $resHier = $curlObj->DoCurl();


        // Guess that the topmost arch id will be the one we want. :\
        $n = preg_match('~\<em\>ARC ID\:\</em\>\s*\<strong\>([\d]+)\</strong\>~isSU', $resHier, $m);
        $meta['recordGroupARC'] = niceify($m[1]);

	$n = preg_match('~\<strong\>Series\:\s*\</strong\>\s*\<span class="hierRecord"\>\s*(.*)\</span\>\s*\<span class="hierlocalid"\>.*\<strong\>\s*([\d]+)\s*\</strong\>~isSU', $resHier, $m);
	$meta['hierSeriesName'] = niceify($m[1]);
	$meta['hierSeriesID'] = niceify($m[2]);

	$n = preg_match('~\<td class="hierFileUnitLink"\>\s*\<span class="hierRecord"\>\s*(.*)\</span\>\s*\<span class="hierlocalid"\>.*\<strong\>\s*([\d]+)\s*\</strong\>~isSU', $resHier, $m);
	$meta['hierFileUnitName'] = niceify($m[1]);
	$meta['hierFileUnitID'] = niceify($m[2]);


	// Find authors if there are any, from the details page.
	$n = preg_match('~\<li\>Contributors to Authorship and/or Production of the Archival Materials\:\</li\>\s*\<ul\>(.*)\</ul\>~isSU', $res, $m);
	if ($n == 0)
	{
		$meta['authors'] = array();
	} else {	
		preg_match_all('~\<li\>\s*<a href="[^"]+\?id\=([\d]+)\&[^"]*relationship\=AD_CONTRIBUTOR[^"]*"\>(.*)\</a\>\s*\</li\>~isSU', $m[1], $sm, PREG_SET_ORDER);
		foreach ($sm as $mNum => $row)
		{
			$meta['authors'][ $row[1] ] = $row[2];			
		}
	}

	// Find geographic subjects if there are any, from the details page.

        if (preg_match_all('~\<a href\="ExecuteRelatedGeographicalSearch[^"]*\?id\=([\d]+)\&[^"]*relationship\=AD_SUBJECT[^"]*"\>(.*)\</a\>~isSU', $res, $sm, PREG_SET_ORDER)) 
        {
                foreach ($sm as $mNum => $row)
                {
                        $meta['places'][ $row[1] ] = $row[2];
			//http://arcweb.archives.gov/arc/action/ExecuteRelatedGeographicalSearch?id=4202085&relationship=AD_SUBJECT
		       $meta['linkToPlace'] = 'http://arcweb.archives.gov/arc/action/ExecuteRelatedGeographicalSearch?id=' . $row[1] . '&relationship=AD_SUBJECT';
		        $curlObj->url = $meta['linkToPlace'];
		        $resPlace = $curlObj->DoCurl();
			if (preg_match('~Coordinates\:\</th\>\s*\<td\>.*\(([\d\.\-]+), ([\d\.\-]+)\)\</td\>~isSU', $resPlace, $ssm))
			{
				$meta['placeCoordinates'][ $row[1] ] = array(
					'lat' => $ssm[1],
					'long' => $ssm[2]
				);				
			} else {
			}
			

                }
        } else {
                $meta['places'] = array();
        }

	/*
		<tr>
		<th valign="top">Type(s) of Archival Materials:</th><td>Textual Records</td>
		</tr>
	*/

	$n = preg_match_all('~<tr>\s*<th valign="top">\s*(.+)</th><td>(.+)</td>\s*</tr>~isSU', $res, $m, PREG_SET_ORDER);
	//var_dump($m);

	//exit;

	foreach ($m as $mNum => $mArr)
	{
		$key = trim($mArr[1]);
		$niceKey = niceify($key);
		$val = trim($mArr[2]);
		$niceVal = niceify($val);

		switch($niceKey) {
			case 'Creator(s):':
				$cleaned = preg_replace('~[\r\n]{2}~i', "\n", $niceVal);
				$cleaned = nl2br($cleaned);
				$meta['creatorsNice'] = $niceVal;
				$meta['creatorsCleaned'] = $cleaned;
				break;
			case 'Type(s) of Archival Materials:':
				break;
			case 'Contact(s):':
				//{contactsField}
				$meta['contactsNice'] = $niceVal;
                                $cleaned = preg_replace('~(phone|fax)\:\s*[^\s\;]+[\s\;]+~isSU', '', $niceVal);
                                $cleaned = preg_replace('~(email)\:.*$~isSU', '', $cleaned);
                                $meta['contactsNicer'] = trim(niceify($cleaned));
				break;
			case 'Broadcast Date(s):':
			case 'Coverage Dates:':
			case 'Coverage date(s):':
			case 'Release date(s)':
			case 'Copyright date(s)':
			case 'Production Date(s):':
				//{productionDateNice}
				$meta['productionDateNice'] = $niceVal;
				$cleaned = preg_replace('~([\d]+)/([\d]+)/([\d]+)~', '{{date|\3|\1|\2}}', $niceVal);
				$meta['productionDateNicer'] = $cleaned;
				//$meta['productionDateNicer'] = '{{date|' . date('Y|m|d', strtotime($niceVal)) .'}}';
				break;
			case 'Part Of:':
				//{partOfID} - needs id from the url.
				//{partOfNice}
				$m = preg_match('~.*id=([\d]+)&~isSU', $val, $mr);
				$meta['partOfID'] = $mr[1];
				$meta['partOfNice'] = $niceVal;
				break;
			case 'Access Restriction(s):':
				break;
			case 'Use Restriction(s):':
				break;
			case 'Variant Control Number(s):':
				//{variantControlNumbersNice}
				$meta['variantControlNumbersNice'] = $niceVal;
				$meta['variantControlNumbersRaw'] = $val;
				$cleaned = preg_replace('~\<br\>~i', "<br />\n", $val);
				$meta['variantControlNumbersBR2NL'] = $cleaned;
				break;
			case 'General Note(s):':
				$meta['genNotes'] = $niceVal;
			default:
				break;

		}
		$metaData[$key] = $val;
	}
	/*var_dump($metaData);
	echo "-----------------------------------------------\n";
	var_dump($meta);
	exit;
	*/

	$MTEMP->assign('md', $meta);
	$MTEMP->display('archives.t');
	return;


	$results = array_reverse($results['revisions'], true);

	if (!empty($_GET['revid']))
	{
		$_GET['revid'] = (int) $_GET['revid'];
		// ... just in case anyone tries any shenanigans to break urls and stuff. :P
	}

	if (empty($results))
	{
		$MTEMP->assign('results', array());
		$MTEMP->display('3rr.t');
		return;
	} else {
		$MTEMP->assign('results', $results);
		$MTEMP->display('3rr.t');
		return;
	}

}

function ResetCurl() {
        global $curlObj, $CONFIG;

        $curlObj = NULL;
        $curlObj = new quickcurl();
        //$curlObj->url = $CONFIG['apiUrl'];
        $curlObj->xlateAfter = false;   // don't fix stuff, it'll just break serialization.
}



?>
