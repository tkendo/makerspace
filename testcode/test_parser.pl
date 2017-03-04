my $file = "test_out";

open $FH, "<", $file;

$trans = 0;
$rcv = 0;
$time = 0;
$i = 1;

while ( my $line = <$FH> ) {
    if ( $line =~ /(\d{1,2}) packets transmitted, (\d{1,2}) received, (\d{1,3})% packet loss, time (\d{1,4})/ )
    {
        $trans = $trans + $1;   
        $rcv = $rcv + $2; 
     #   $time = $time + $4;
     #   $i = $i + 1;
    }
    if ( $line =~ /rtt min\/avg\/max\/mdev = (.+)\/(.+)\/(.+)\/(.+)/ )
    {
        $time = $time + $2;
        $i = $i + 1;
    }
}

$loss = ( ( 1 - $rcv / $trans) * 100);
$time = $time / $i;
printf ( "transmitted: $trans\nrcv: $rcv\navg pack loss: %.5f%\navg time: $time ms\n", $loss );
