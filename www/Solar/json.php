<?php
error_reporting(-1);
if (!include("config.php"))
    die("{\"error\": \"config.php not found! Copy config.example.php for a template.\"}");
if (!include("functions.php"))
    die("{\"error\": \"functions.php not found!\"}");
if (!include("solar.php"))
    die("{\"error\": \"solar.php not found!\"}");

mysql_connect($db_host, $db_user, $db_password) or die("{\"error\": \"Could not connect to database!\"}");
mysql_select_db($db_database) or die("{\"error\": \"Could not find database!\"}");



$action = isset($_GET['action']) ?  $_GET['action'] : 'stats';

if ($action == 'stats'):
    $data = get_solar_data();
    $i = 0;
?>
    {"data": [
    <?php foreach ($data as $table => $tdata): ?>

    <?php if ($i++ > 0) echo ","; ?>

    {"time": 		"<?php echo $tdata['current_data']->time; ?>",
     "flags": 		"<?php echo flags2html($tdata['current_data']->flags); ?>",
     "pv_volt": 	<?php echo $tdata['current_data']->pv_volt / 10.; ?>,
     "pv_amp": 		<?php echo $tdata['current_data']->pv_amp / 100.; ?>,
     "grid_freq": 	<?php echo $tdata['current_data']->grid_freq / 100.; ?>,
     "grid_volt": 	<?php echo $tdata['current_data']->grid_volt; ?>,
     "grid_pow": 	<?php echo $tdata['current_data']->grid_pow; ?>,
     "total_pow": 	<?php echo $tdata['current_data']->total_pow / 100.; ?>,
     "temp": 		<?php echo $tdata['current_data']->temp; ?>,
     "peak_temp":    <?php echo $tdata['peak_temp']; ?>,
     "optime": 		"<?php echo mins2verbose($tdata['current_data']->optime); ?>",
     "hasdata": 	<?php echo $tdata['current_data']->hasdata; ?>,
     "peak_pow":    <?php echo $tdata['peak_pow']; ?>,
     "today_pow":   <?php echo $tdata['today_pow']; ?>,
     "money":       <?php echo sprintf('%.2f', 0.0/*$money*/); ?>,
     "money_today": <?php echo sprintf('%.2f', 0.0/*$money_today*/); ?>}
     
    <?php endforeach; ?>
    ]}
    <?php
elseif ($action == 'day'):
    $year = isset($_GET['year']) ? $_GET['year'] : 2011;
    $year = mysql_real_escape_string($year);
    $month = isset($_GET['month']) ? $_GET['month'] : 7;
    $month = mysql_real_escape_string($month);

    $pow = Array();
    $peak = Array();
    foreach ($db_tables_solar as $table) {
        list($tpow, $tpeak) = get_solar_daymode($table, $month, $year);
        $pow[] = '[' . implode(', ', $tpow) . ']';
        $peak[] = '[' . implode(', ', $tpeak) . ']';
    }
    
    ?>
    {
     "year":    <?php echo $year; ?>,
     "month":   <?php echo $month; ?>,
     "pow":     [<?php echo implode(', ', $pow); ?>],
     "peakpow": [<?php echo implode(', ', $peak); ?>]
    }
    <?php    
elseif ($action == 'week'):
    $year = isset($_GET['year']) ? $_GET['year'] : 2011;
    $year = mysql_real_escape_string($year);

    $data = Array();
    foreach ($db_tables_solar as $table)
        $data[] = get_solar_weekmode($table, $year);
    
    ?>
    {"year":    <?php echo $year; ?>,
     "data":    [<?php echo implode(', ', $data); ?>]}
    <?php
elseif ($action == 'month'):
    $year = isset($_GET['year']) ? $_GET['year'] : 2011;
    $year = mysql_real_escape_string($year);

    $data = Array();
    foreach ($db_tables_solar as $table)
        $data[] = get_solar_monthmode($table, $year);
    
    ?>
    {"year":    <?php echo $year; ?>,
     "data":    [<?php echo implode(', ', $data); ?>]}
    <?php
elseif ($action == 'year'):
    $year = isset($_GET['year']) ? $_GET['year'] : 2011;
    $year = mysql_real_escape_string($year);

    $data = Array();
    foreach ($db_tables_solar as $table)
        $data[] = get_solar_yearmode($table, $year);
    
    ?>
    {"year":    <?php echo $year; ?>,
     "data":    [<?php echo implode(', ', $data); ?>]}
    <?php
elseif ($action == 'resol'):
    $res = mysql_query(
    "SELECT `time`, `t1`, `t2`, `t3`, `p1`
    FROM `$db_table_resol`
    WHERE DATEDIFF(CURDATE(), `time`) < 2
    ORDER BY `time`");
    if (!$res) die('{"error": "'.mysql_error().'"}');
    // Same as first one: we need starting data and stuff
    $row = mysql_fetch_object($res);
    if (!$row) die("{\"error\": \"No data!\"}");
    $ts =       explode(" ", $row->time);
    $ts_date =  explode("-", $ts[0]);
    $ts_time =  explode(":", $ts[1]);
    $ts_year =  $ts_date[0];
    $ts_month = $ts_date[1]-1; // JS months are zero based... seriously...?
    $ts_day =   $ts_date[2];
    $ts_hour =  $ts_time[0];
    $ts_min =   $ts_time[1];
    $ts_sec =   $ts_time[2];
    $t1_data = Array($row->t1/10.);
    $t2_data = Array($row->t2/10.);
    $t3_data = Array($row->t3/10.);
    $p1_data = Array($row->p1);
    while ($row = mysql_fetch_object($res)) {
        $resol_t1_data[] = $row->t1/10.;
        $resol_t2_data[] = $row->t2/10.;
        $resol_t3_data[] = $row->t3/10.;
        $resol_p1_data[] = $row->p1;
    }
    
    $res = mysql_query("
    SELECT `time`, `t1`, `t2`, `t3`, `p1`
    FROM `$db_table_resol`
    ORDER BY `time` DESC
    LIMIT 1");
    if (!$res) die('{"error": "'.mysql_error().'"}');
    $current_data = mysql_fetch_object($res);
    if (!$current_data) die("{\"error\": \"No data!\"}");
    
    // Why are all those things casted to an int, you may ask? Otherwise, it may
    // send a value as '00' (two zeroes). The JSON thing of jQuery hates this,
    // and silently ignores the entire response.
    ?>
    {"year":     <?php echo (int)$ts_year; ?>,
     "month":    <?php echo (int)$ts_month; ?>,
     "day":      <?php echo (int)$ts_day; ?>,
     "hour":     <?php echo (int)$ts_hour; ?>, 
     "min":      <?php echo (int)$ts_min; ?>,
     "sec":      <?php echo (int)$ts_sec; ?>,
     "p1":       [<?php echo implode(',', $resol_p1_data); ?>],
     "t1":       [<?php echo implode(',', $resol_t1_data); ?>],
     "t2":       [<?php echo implode(',', $resol_t2_data); ?>],
     "t3":       [<?php echo implode(',', $resol_t3_data); ?>],
     "cur_time": "<?php echo $current_data->time; ?>",
     "cur_t1":   <?php echo $current_data->t1 / 10.; ?>,
     "cur_t2":   <?php echo $current_data->t2 / 10.; ?>,
     "cur_t3":   <?php echo $current_data->t3 / 10.; ?>,
     "cur_p1":   <?php echo $current_data->p1; ?>}
     
    <?php    
else:
    die("{\"error\": \"Unkown action '$action'\"}");
endif;
?>
