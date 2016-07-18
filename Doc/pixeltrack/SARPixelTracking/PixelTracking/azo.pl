#!/usr/bin/perl
### offset.pl

$] >= 5.004 or die "Perl version must be >= 5.004 (Currently $]).\n";

use Env qw(INT_SCR INT_BIN);
use lib "$INT_SCR";  #### Location of Generic.pm
use lib "$OUR_SCR";  #### Location of Generic.pm
use Generic;

###Usage info/check
sub Usage{

`$INT_SCR/pod2man.pl  $INT_SCR/azo.pl`;
exit 1;
}
@ARGV >= 6 or Usage();
@args = @ARGV;

$file1         = shift;
$file2         = shift;
$cull0pre      = shift;
$outoffpre     = shift;
$window_size_x = shift;
$window_size_y = shift;
$skip_factor   = shift or $skip_factor = 1;
$nproc         = shift or $nproc = 1;

$outoffpre2     = "${outoffpre}${window_size_x}x${window_size_y}";

#################
Message "Checking I/O";
#################
#@Infiles  = ($file1, $file2, "$cull0pre.off", "$file1.rsc", "$file2.rsc");
#@Outfiles = ("");
#&IOcheck(\@Infiles, \@Outfiles);
Log("azo.pl", @args);

#################
Message "Reading resource file: $file1.rsc";
#################
$orbit_number       = Use_rsc "$file1 read ORBIT_NUMBER";
$width              = Use_rsc "$file1 read WIDTH";
$length_1           = Use_rsc "$file1 read FILE_LENGTH";
$date1              = Use_rsc "$file1 read DATE";

######################################
Message "Reading resource file: $file2.rsc";
######################################
$orbit_number_2 = Use_rsc "$file2 read ORBIT_NUMBER"; 
$width_2        = Use_rsc "$file2 read WIDTH";  
$date2          = Use_rsc "$file2 read DATE";

$length=$length_1;

#################################################
Message "Writing resource file: $outoffpre.off.rsc";
#################################################
Use_rsc "$outoffpre.off write ORBIT_NUMBER $orbit_number-$orbit_number_2";
Use_rsc "$outoffpre.off write DATE12 $date1-$date2";
Use_rsc "$outoffpre.off merge $file1";

##################################
Message "Get median offset from $cull0pre.off";
##################################

open CULL, "$cull0pre.off" or
die "Can't open $cull0pre.off\n";

while (<CULL>){
  @line = split /\s+/, $_;
  push @X, $line[2];
  push @Y, $line[4]; 
}
close (CULL);

@X = sort @X;
@Y = sort @Y;

$X0= Median(\@X);
$Y0= Median(\@Y);

$iY0 = int($Y0);
$iX0 = int($X0);

##########################################
Message "Preparing input values";
##########################################

$datatype        = "cpx";
$oversample_fact = 64; #will give 128th of a pixel max accuracy
$window_size     = 8;
$snr_thresh      = 0; 
$cov_thresh      = 1e10;

$pix_ave_x = 1; #dont screw with this
$pix_ave_y = 1; #dont screw with this

$skip_x = int($window_size_x/$skip_factor);
$skip_y = int($window_size_y/$skip_factor);
$search_x = 8;
$search_y = 8;

for ($iproc=1; $iproc <= $nproc; $iproc++){

##########################################
  Message "Running offsets, iproc=$iproc";
##########################################

  $lines_proc = int($length/$nproc/$window_size_y)*$window_size_y;

  if ($iY0 < 0) {$yoffset = int(-$Y0);}
  $yoffset or $yoffset = 0;

  $firstline = ($iproc-1)*$lines_proc+1+int($window_size_y/2)+$yoffset; #start defined by 1/2 window down plus gross offset
  $lastline  = $firstline+$lines_proc-1;

  if ($iX0 < 0) {$firstpix = int(1-$X0);}
  $firstpix or $firstpix = 1;

  $parfile = "${outoffpre2}_${iproc}.in";
  $azofile = "${outoffpre2}_${iproc}.off";
  $outfile = "${outoffpre2}_${iproc}.out";

  open (OFF, ">$parfile") or die "Can't write to $parfilen\n";
  print OFF <<END;
                 AMPCOR INPUT FILE

DATA TYPE

Data Type for Reference Image Real or Complex                   (-)    =  Complex   ![Complex , Real , RMG1 , RMG2]
Data Type for Search Image Real or Complex                      (-)    =  Complex   ![Complex , Real , RMG1 , RMG2]
                                                                          !If file is a line interleaved (i.e. RMG)
                                                                          !file then RMG1 one uses the first data 
                                                                          !layer and RMG2 uses the secoond data layer

INPUT/OUTPUT FILES

Reference Image Input File                                      (-)    =  $file1
Search Image Input File                                         (-)    =  $file2
Match Output File                                               (-)    =  $azofile

MATCH REGION

Number of Samples in Reference/Search Images                    (-)    =  $width $width_2 !Must be less than 18000

Start, End and Skip Lines in Reference Image                    (-)    =  $firstline $lastline $skip_y

Start, End and Skip Samples in Reference Image                  (-)    =  $firstpix $width $skip_x
                                                                          !Provides location of match windows in
                                                                          !imagery. Note it is possible to match with 
                                                                          !skip setting less than the window size, of 
                                                                          !course the matches will NOT be independent.

MATCH PARAMETERS

Reference Window Size Samples/Lines                             (-)    =  $window_size_x $window_size_y

Search Pixels Samples/Lines                                     (-)    =  $search_x $search_y
                                                                          !ref window size plus plus 2*(search window size)
                                                                          !must be less than 512. Note to get best
                                                                          !oversampling of the correlation surface should
                                                                          !set the search window to 8 or greater, otherwise
                                                                          !sinc interpolator does not have enough support.

Pixel Averaging Samples/Lines                                   (-)    =  $pix_ave_x $pix_ave_y
                                                                          !If you expect subpixel matching accuracy
                                                                          !then this SHOULD BE SET TO ONE!

Covariance Surface Oversample Factor and Window Size            (-)    =  $oversample_fact $window_size
                                                                          !oversample factor determine how much
                                                                          !oversampling via sinc interpolation is done
                                                                          !for the covariance surfcae. Two times this
                                                                          !number is the quantization level of the matches,
                                                                          !e.g. if oversample = 64 the 128 of a pixel
                                                                          !quantization error. Window size is how many pixels
                                                                          !in the CORRELATION SURFACE to oversample. Best
                                                                          !results should have number >= 8.

Mean Offset Between Reference and Search Images Samples/Lines   (-)    =  $iX0 $iY0
                                                                          !Convention used is that position in ref image plus
                                                                          !offset is equal to position in image 2.  

MATCH THRESHOLDS AND DEBUG DATA

SNR and Covariance Thresholds                                   (-)    =  $snr_thresh $cov_thresh
                                                                          !Eliminates matches based on SNR threshold (SNR must be
                                                                          !greater than this threshold) and Covariance threshold
                                                                          !(cross track and along track SQRT(COV) must be LESS THAN
                                                                          !than this threshold in PIXELS. Typical values depend
                                                                          !on type of imagery being matched. 

Debug and Display Flags T/F                                     (-)    =  f f
END
    close(OFF);

################################################################

Message "$INT_BIN/ampcor $parfile rdf > $outfile";
unless($iproc==$nproc){
system("$INT_BIN/ampcor $parfile rdf > $outfile &");
}
if($iproc==$nproc){
system("$INT_BIN/ampcor $parfile rdf > $outfile");
}

}

=pod

=head1 USAGE

B<azo.pl> I<file1 file2 bla bla bla>

=head1 FUNCTION

Computes the offset field between two files

=head1 ROUTINES CALLED

ampcor_new

=head1 CALLED BY

=head1 FILES USED

I<file1>

I<file1>.rsc

I<file2>

I<file2>.rsc

=head1 FILES CREATED

I<offsetfile>.off

I<offsetfile>.off.rsc

I<offsetfile>.in

I<offsetfile>.out

=head1 HISTORY

=head1 LAST UPDATE


=cut
