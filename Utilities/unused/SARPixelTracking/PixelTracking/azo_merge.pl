#!/usr/bin/perl
### offset.pl


###Usage info/check
sub Usage{

`$INT_SCR/pod2man.pl  $INT_SCR/azo_merge.pl`;
exit 1;
}
@ARGV == 1 or Usage();
@args = @ARGV;

$azopre = shift;

$ascfile = "$azopre.off";
$binfile = "$azopre.off.bin";

$tmpfile = "tmp.off";

`touch $tmpfile`;
`cat ${azopre}*.off >> $tmpfile`;

open TMP, "$tmpfile"  or die "Can't read $tmpfile\n";
open ASC, ">$ascfile" or die "Can't write to $ascfile\n";
open BIN, ">$binfile" or die "Can't write to $binfile\n";

while ($line=<TMP>){
  unless($line =~ /\*/) {
    print ASC $line;
    chomp $line;
    $line=~s/^\s+//;
    $string = pack("f" x 8,(split /\s+/, $line)); #split and convert to bin
    print BIN $string;
  }
}

close (TMP);
close (ASC);
close (BIN);

`rm -f $tmpfile`;
#`rm -f ${azopre}_*`;

exit 0;


=pod

=head1 USAGE

B<azo_run_one.pl> I<parfile azofile outfile process_num>

=head1 FUNCTION

Computes the offset field between two files

=head1 ROUTINES CALLED

ampcor

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
