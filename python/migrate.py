 SELECT game_server_list.game_id, game_plat_info.plat_cname, game_server_list.server_id, db_server_list.server_ip, db_server_list.db_port, physical_server_list.server_ip,game_server_list.openday
FROM game_plat_info, game_server_list, db_server_list, physical_server_list
WHERE game_plat_info.id = game_server_list.plat_id
AND game_server_list.db_server_id = db_server_list.id
AND game_server_list.physical_server_id = physical_server_list.id
AND game_server_list.plat_cname = 'uc'
AND game_server_list.server_id =1
AND game_server_list.game_id =1
LIMIT 0 , 30 
