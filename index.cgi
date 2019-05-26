#!/usr/bin/perl

use CGI ':standard';
use POSIX 'strftime';
use GD;
use Locale::Country;

#Load parameters from the browser
$filename = param('filename');
$invert = param('invert');
$i = param('image');

#Prevent all and any form of caching, so the user don't get stale data
print "Expires: Sat, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: ".strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime)."\n";
print "Pragma: no-cache\n";
print "Cache-Control: private, no-cache, no-store, must-revalidate, max-age=0, pre-check=0, post-check=0\n";

#If user don't request a image, send the HTML page
if ($i ne "1") {
	print "Content-Type: text/html\n\n";
	print "<html><head><title>OpenHack SIDA Project</title></head><body>";
	print "<form><select name='filename'>";
	opendir(DIR, "openaid");
	while ($file = readdir(DIR)) { #Load all CSV files into a <select>
		next if ($file =~ m/^\./);
		if ($filename eq $file) {
			print "<option value='".$file."' selected>".$file."</option>";
		}
		else
		{
			print "<option value='".$file."'>".$file."</option>";
		}
	}
	closedir(DIR);
	print "</select><br>Invert: <input type='checkbox' name='invert' value='1'";
	if ($invert eq "1") {
		print " checked";
	}
	print "> <input type='submit'></form>";
	if ($filename) {
		print "<img src='index.cgi?image=1&invert=".$invert."&filename=".$filename."' width='1125px' height='558px'>";
	}
	print "</body></html>";
}

#If filename has been given (selected) and user is requesting a image.
if (($filename)&&($i eq "1")) {

	open(CFILE, "data.txt"); #Load country data (with country name + image coordinate)
	flock(CFILE,1);
	@content = <CFILE>;
	close(CFILE);

	%countrytable = ();
	%cpitable = ();
	%sums = ();

	foreach $cline (@content) {
	($countryname, $countrycode, $coordx, $coordy, $garbage) = split(";",$cline);
		if (($countryname)&&($countrycode)&&($coordx)&&($coordy)) {
			$countrytable{$countrycode} = $countryname.":".int($coordx).":".int($coordy);
		}
	}

	open(CPIFILE, "cpi.csv"); #Load corruption perception index file
	@cpidata = <CPIFILE>;
	close(CPIFILE);

	foreach $entry (@cpidata) {
		($cpiname, $cpicode, $garbage, $cpiscore, $garbage) = split(";", $entry);
		unless (($cpiname =~ m/Corruption/)||($cpiname eq "")||($cpiname eq "Country")) {
			if (($cpiname)&&($cpicode)&&($cpiscore)) {
				$cpitable{$cpicode} = $cpiscore;
			}
		}
	}

	%sums = scrubfile($filename);

	#Create a score of 0-100 (0r 100-0 if inverted is chosen) from low to high donations of money.
	$highestsum = 0;
	%weights = ();

	foreach $k (keys %sums) {
		if ($sums{$k} > $highestsum) {
			$highestsum = $sums{$k};
		}
	}


	foreach $k (keys %sums) {
		$wval = int(($sums{$k} / $highestsum) * 100);
		if ($invert eq "1") {
			$weights{$k} = 100 - $wval;
		}
		else
		{
			$weights{$k} = $wval;
		}
	}

	#Create a 0-100 score out of corruption index. This is mainly done because if a small CSV source is set, it can be good to spread out the values a bit.
	$highestcpi = 0;
	%cpiweights = ();

	foreach $k (keys %sums) {
		if ($cpitable{$k} > $highestcpi) {
			$highestcpi = $cpitable{$k};
		}
	}


	foreach $k (keys %sums) {
		$wval = int(($cpitable{$k} / $highestcpi) * 100);
		$cpiweights{$k} = $wval;
	}
	#Create the image
	$image = GD::Image->newFromPng("world.png");
	foreach $c (keys %weights) {
		($cname, $cx, $cy) = split(":", $countrytable{$c});
		($red, $green, $blue) = weight($weights{$c}, $cpiweights{$c}); #Weight both countries and paint the country according to the scale
		$lc = $image->colorAllocate($red,$green,$blue);
		$image->fill($cx,$cy,$lc);
	}
	print "Content-Type: image/png\n\n"; #output the image to browser.
	binmode(STDOUT);
	print $image->png;

}

#Function that weights 2 values between 0-100 against each other and return a color closer to red or blue for a imbalance,
#and closer to green for a balance.
sub weight() {
	$bowla = $_[0];
	$bowlb = $_[1];

	$result = $bowlb - $bowla;

	if ($result < 0) {
		$result = $result * -1;
		$r = 2.55 * $result;
		$g = 2 * (100 - $result);
		$b = 0;
	}
	else
	{
		$b = 2.55 * $result;
		$g = 2 * (100 - $result);
		$r = 0;
	}
	return(int($r), int($g), int($b));
}

#Function that cleans a OpenAid CSV from erronous and bad quality data
sub scrubfile() {
	$filename = $_[0];
	%totalsum = ();
	open(TOSCRUB, "openaid/".$filename);
	@fcontent = <TOSCRUB>;
	close(TOSCRUB);
	$finishedline = "";
	foreach $l (@fcontent) {
		$l =~ s/\n//sgi; #Delete linebreaks, tabs and spaces from the CSV data
		$l =~ s/\r//sgi;
		$l =~ s/\t//sgi;
		$l =~ s/ //sgi;
		if ($l =~ m/^(D|3),Disbursement,/) { #If we find a new data line, parse the line before completely
			if (length($finishedline) > 0) { #If we have read in data on previous iterations
				$finishedline =~ s/\"([^"]*)\"//sgi; #Delete long explanations and organization names from CSV (not interested in them anyways)
				($gar,$gar,$gar,$dollaramount,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$cc1,$cc2,$gar) = split(",", $finishedline);
				if ((length($cc1) == 2)&&($cc1 =~ m/^[A-Z]*$/)) { #OpenAid data seem to mix Version 1.05 with Version 2.00+, so we need to cater for both
					$countrycode = $cc1;
				}
				else
				{
					$countrycode = $cc2;
				}
				$countrycode = uc(country_code2code($countrycode,LOCALE_CODE_ALPHA_2, LOCALE_CODE_ALPHA_3)); #Convert to 3-digit ISO code as CPI uses 3-digit
				if ((length($countrytable{$countrycode}) > 1)&&($dollaramount)&&(substr($dollaramount, 0, 1) ne "-")) { #Sort out negative values because money going in the other direction, we are not interested in.
					$totalsum{$countrycode} = $totalsum{$countrycode} + $dollaramount;
				}
			}
			$finishedline = $l; #Start on a new entry
		}
		else
		{
			if (length($finishedline) > 0) {
				$finishedline = $finishedline . $l; #We are still on the old entry, continue reading
			}
		}
	}
	#Same as in loop, but executed a last time in case we started on a entry but didn't yet finish it, lets finish it here.
	if (length($finishedline) > 0) {
		$finishedline =~ s/\"([^"]*)\"//sgi;
		($gar,$gar,$gar,$dollaramount,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$cc1,$cc2,$gar) = split(",", $finishedline);
		if ((length($cc1) == 2)&&($cc1 =~ m/^[A-Z]*$/)) {
			$countrycode = $cc1;
		}
		else
		{
			$countrycode = $cc2;
		}
		$countrycode = uc(country_code2code($countrycode,LOCALE_CODE_ALPHA_2, LOCALE_CODE_ALPHA_3));
		if ((length($countrytable{$countrycode}) > 1)&&($dollaramount)&&(substr($dollaramount, 0, 1) ne "-")) {
			$totalsum{$countrycode} = $totalsum{$countrycode} + $dollaramount;
		}
	}
	return %totalsum;
}
