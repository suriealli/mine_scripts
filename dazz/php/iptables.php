<?php
require_once ('header.php');
require_once ('phpcommon/mysqlfunctions.php');
require_once ('phpcommon/mysqlproxy.php');

$RES_DB_HOST="42.62.29.179";
$RES_DB_PORT=62929;
$RES_DB_USER="root";
$RES_DB_PWD="UQEnZcVXdjzA3uZC";

$db_link_admin = CreateConnect($RES_DB_HOST,$RES_DB_USER,$RES_DB_PWD,$RES_DB_PORT,"uc_41_ssqy_game","utf8");

$strsql = 'select * from role_name_map where role_id = 1';
$query = $db_link_admin->Query($strsql);
while ($row = $db_link_admin->FetchArray($query)) {
        $fit_server_arr[] = $row;
    }
    if (empty($fit_server_arr)) {
        return;
    }
foreach ($fit_server_arr as $fit_server) {
print_r($fit_server);
}

?>
