<?php
error_reporting(0);
if (!include("config.php"))
    die("config.php not found! Copy config.example.php for a template.");

if (!include("functions.php"))
    die("functions.php not found!");

if (!include("solar.php"))
    die("solar.php not found!");

error_reporting(-1);

mysql_connect($db_host, $db_user, $db_password) or
    die("Could not connect to database!");
mysql_select_db($db_database) or die("Could not find database!");

$data = get_solar_data($db_tables_solar);

$yearrange = Array('lyear' => 9999,
                   'hyear' => 0,
                   'lmonth' => 99,
                   'hmonth' => 0);
foreach ($data as $table => $tdata) {
    if ($yearrange['lyear'] > $tdata['yearrange']->lyear)
        $yearrange['lyear'] = $tdata['yearrange']->lyear;

    if ($yearrange['hyear'] < $tdata['yearrange']->hyear)
        $yearrange['hyear'] = $tdata['yearrange']->hyear;

    if ($yearrange['lmonth'] > $tdata['yearrange']->lmonth)
        $yearrange['lmonth'] = $tdata['yearrange']->lmonth;

    if ($yearrange['hmonth'] < $tdata['yearrange']->hmonth)
        $yearrange['hmonth'] = $tdata['yearrange']->hmonth;
}



?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nl" lang="nl">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />

    <link type="text/css" href="css/smoothness/jquery-ui-1.8.7.custom.css"
        rel="stylesheet" />
    <link type="text/css" href="css/layout.css" rel="stylesheet"/>
    <link type="text/css" href="css/colorbox.css" rel="stylesheet"/>


    <script src="js/jquery-1.4.4.min.js" type="text/javascript"></script>
    <script src="js/jquery-ui-1.8.7.custom.min.js"
        type="text/javascript"></script>
    <script src="js/highcharts.js" type="text/javascript"></script>
    <script src="js/jquery.colorbox-min.js" type="text/javascript"></script>

    <script src="js/solargraphs.js" type="text/javascript"></script>
    <script src="js/imagepopup.js" type="text/javascript"></script>
    <script src="js/navbuttons.js" type="text/javascript"></script>
    <script src="js/refreshdata.js" type="text/javascript"></script>

    <script type="text/javascript">
        // PHP inserts data here
        var lyear = <?php echo $yearrange['lyear']; ?>;
        var hyear = <?php echo $yearrange['hyear']; ?>;
        var lmonth = <?php echo $yearrange['lmonth']  - 1; ?>;
        var hmonth = <?php echo $yearrange['hmonth'] - 1; ?>;

        var month_map = ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni',
            'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'];
        function day_cur_month_length() {
            return new Date(day_cur_year, day_cur_month + 1, 0).getDate();
        }

        var day_cur_month = hmonth;
        var day_cur_year = hyear;
        var week_cur_year = hyear;
        var month_cur_year = hyear;
        var year_cur_year = hyear;

        var power_day_start = [];
        var power_day_data = [];

        var day_total_start = Date.UTC(day_cur_year, day_cur_month, 1);
        var day_total_data = [];
        var day_peak_data = [];

        var week_total_data = [];
        var month_total_data = [];
        var year_total_data = [];

        <?php foreach ($data as $table => $tdata): ?>

        power_day_start.push(Date.UTC(<?php echo $tdata['ts']['year'] . ", " .
                                                 $tdata['ts']['month'] . ", " .
                                                 $tdata['ts']['day'] . ", " .
                                                 $tdata['ts']['hour'] . ", " .
                                                 $tdata['ts']['min'] . ", " .
                                                 $tdata['ts']['sec'] ?>));
        power_day_data.push(
            [
                <?php
                    echo $tdata['ts']['pow'];
                    while ($row = mysql_fetch_object($tdata['today_res'])) {
                        echo ", " . ($row->hasdata ?
                            ($row->grid_pow) : "-30");
                    }
                ?>
            ]);

        day_total_data.push(
            [<?php echo implode(',', $tdata['day_pow_data']); ?>]
        );
        day_peak_data.push(
            [<?php echo implode(',', $tdata['day_peakpow_data']); ?>]
        );

        week_total_data.push(<?php echo $tdata['week_data']; ?>);
        month_total_data.push(<?php echo $tdata['month_data']; ?>);
        year_total_data.push(<?php echo $tdata['year_data']; ?>);

        <?php endforeach; ?>

        // Create the JS tabs
        $(document).ready(function() {
            $("#tabs").tabs();
        });
    </script>

    <title>Zonnepanelen data</title>
</head>
<body>
    <div id="wrapper">
        <div id="header">
            <h1>Zonnecellen data</h1>
        </div>

        <div id="notify">
            <noscript>
                <div class="error">
                    Javascript needs to be turned on for this page.
                </div>
            </noscript>

            <!--[if lt IE 7]>
                <div class="error">
                    Internet Explorer 6 and lower is not supported.
                </div>
            <![endif]-->
        </div>

        <div id="intro">
            <p>
                Hieronder de gegevens van een van onze zonnecollectoren op het dak.
                Het is de bedoeling dat de gegevens van de tweede ook toegevoegd worden.
            </p>
            <p>
            	Open <a href="./grafieken/index.html" target="_blank">deze link</a> om het verloop in grafieken te zien welke op basis van CSV bestanden gemaakt worden.
            </p>
            <p>
            	Open <a href="http://pvoutput.org/comparelive.jsp?sid=20378&sid1=21351" target="_blank">deze link</a> om het verloop in PVOutput te zien.
            </p>
        </div>

        <!-- jQuery ui styles this to clickable tabs -->
        <div id="tabs">
            <ul>
                <li><a href="#tab_g_detailpower">Vermogen</a></li>
                <li><a href="#tab_g_daytotals">Dag totaal</a></li>
                <li><a href="#tab_g_weektotals">Week totaal</a></li>
                <li><a href="#tab_g_monthtotals">Maand totaal</a></li>
                <li><a href="#tab_g_yeartotals">Jaar totaal</a></li>
                <li><a href="#tab_t_current">Huidige status</a></li>
            </ul>
            <div id="tab_g_detailpower">
                <div id="power_day" style="width: 800px; height: 400px"></div>
            </div>
            <div id="tab_g_daytotals">
                <div id="power_total" style="width: 800px; height: 400px"></div>

                <table class="period_nav" id="day_month_nav">
                    <tr>
                        <td><a href="#" id="day_month_nav_prev">&larr;</a></td>
                        <td id="day_month_nav_cur">Januari</td>
                        <td><a href="#" id="day_month_nav_next">&rarr;</a></td>
                    </tr>
                </table>

                <table class="period_nav" id="day_year_nav">
                    <tr>
                        <td><a href="#" id="day_year_nav_prev">&larr;</a></td>
                        <td id="day_year_nav_cur">2011</td>
                        <td><a href="#" id="day_year_nav_next">&rarr;</a></td>
                    </tr>
                </table>

                <div class="clear"></div>
            </div>
            <div id="tab_g_weektotals">
                <div id="week_total" style="width: 800px; height: 400px"></div>

                <table class="period_nav" id="week_year_nav">
                    <tr>
                        <td><a href="#" id="week_year_nav_prev">&larr;</a></td>
                        <td id="week_year_nav_cur">2011</td>
                        <td><a href="#" id="week_year_nav_next">&rarr;</a></td>
                    </tr>
                </table>

                <div class="clear"></div>

            </div>
            <div id="tab_g_monthtotals">
                <div id="month_total" style="width: 800px; height: 400px"></div>

                <table class="period_nav" id="month_year_nav">
                    <tr>
                        <td><a href="#" id="month_year_nav_prev">&larr;</a></td>
                        <td id="month_year_nav_cur">2011</td>
                        <td><a href="#" id="month_year_nav_next">&rarr;</a></td>
                    </tr>
                </table>

                <div class="clear"></div>

            </div>
            <div id="tab_g_yeartotals">
                <div id="year_total" style="width: 800px; height: 400px"></div>

                <table class="period_nav" id="year_year_nav">
                    <tr>
                        <td><a href="#" id="year_year_nav_prev">&larr;</a></td>
                        <td id="year_year_nav_cur">2011</td>
                        <td><a href="#" id="year_year_nav_next">&rarr;</a></td>
                    </tr>
                </table>

                <div class="clear"></div>

            </div>
            <div id="tab_t_current">
                <div id="cur_intro">Actuele data</div>
                <br class="clear" />

                <div id="stats_solar">
                    <table>
                        <tr>
							<td></td>
                            <td><b>Soladin 2 (tussenmuur)</b></td>
                            <td><b>Soladin 1 (binnenmuur)</b></td>
                        </tr>
                        <tr>
                            <td>Datum/Tijd</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_time">
                                <?php
                                    echo $tdata['current_data']->time;
                                ?>
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>PV voltage</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_pv_volt">
                                <?php
                                    echo $tdata['current_data']->pv_volt / 10.;
                                 ?> V
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>PV amperage</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_pv_amp">
                                <?php
                                    echo $tdata['current_data']->pv_amp / 100.;
                                ?> A
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Grid frequentie</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_grid_freq">
                                <?php
                                    echo $tdata['current_data']->grid_freq
                                        / 100.;
                                ?> Hz
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Grid voltage</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_grid_volt">
                                <?php
                                        echo $tdata['current_data']->grid_volt;
                                ?> V
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Grid vermogen</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_pow">
                                <span class="ct_grid_pow">
                                <?php
                                    echo $tdata['current_data']->grid_pow;
                                ?> W
                                </span>
                                <span class="ct_peak_pow add_today">
                                <?php
                                    echo $tdata['peak_pow'];
                                ?> W piek vandaag
                                </span>
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Totaal vermogen</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_tpow">
                                <span class="ct_total_pow">
                                <?php
                                    echo $tdata['current_data']->total_pow
                                        / 100.;
                                ?> kWh
                                </span>
                                <span class="ct_today_pow add_today">
                                <?php
                                    echo $tdata['today_pow'];
                                ?> kWh vandaag
                                </span>
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Opbrengst euro's</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td>
                                <span class="ct_total_money">
                                    &euro;
                                    <?php
                                        echo sprintf('%.2f', $tdata['money']);
                                    ?>
                                </span>
                                <span class="ct_today_money add_today">
                                    &euro;
                                    <?php
                                        echo sprintf('%.2f',
                                            $tdata['money_today']);
                                    ?>
                                    vandaag
                                </span>
                            </td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Temperatuur</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_temp">
                                <?php
                                    echo $tdata['current_data']->temp;
                                ?> graden Celsius
                            </span>
                                <span class="ct_today_temp add_today">
                                <?php
                                    echo $tdata['peak_temp'];
                                ?> graden piek vandaag
                                </span>
                            </td>
                            <?php endforeach; ?>
                        </tr>
                        <tr>
                            <td>Tijd actief</td>
                            <?php foreach ($data as $t => $tdata): ?>
                            <td><span class="ct_optime">
                                <?php
                                    echo mins2verbose(
                                        $tdata['current_data']->optime);
                                ?>
                            </span></td>
                            <?php endforeach; ?>
                        </tr>
                    </table>
                </div>

                <br class="clear" />


                <?php $flags_res = $data[$db_tables_solar[0]]['flags_res']; ?>

                <?php if (mysql_num_rows($flags_res)): ?>
                <table id="flagstable" style="margin-top: 30px;">
                    <tr>
                        <th colspan="3">Laatste meldingen Soladin</th>
                    </tr>

                    <?php while ($row = mysql_fetch_object($flags_res)): ?>
                        <tr>
                            <td><?php echo $row->time; ?></td>
                            <td>#<?php echo $row->num; ?></td>
                            <td><?php echo flags2html($row->flags); ?></td>
                        </tr>
                    <?php endwhile; ?>

                </table>
                <?php endif; ?>
            </div>
        </div>
        <div id="footer">

            <!--<a href="http://websvn.chozo.nl/listing.php?repname=dump&path=%2FWeb%2Fsolar%2F">Source code</a><br />
            <a href="http://git.chozo.nl/solar.git/">Source code</a><br /> -->
            Made by <a href="http://chozo.nl/">Chozo.nl</a>, changed by <a href="http://lusc.nl/">Lusc.nl</a>
        </div>
    </div>
</body>
</html>

