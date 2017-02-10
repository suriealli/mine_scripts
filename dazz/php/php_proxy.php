<?php 
	
	// $url = 'http://3dgame.manager.com/api/MPush.php';
	$url = 'http://proxy.test.q-dazzle.com/index.php';
	$post_arr['message'] = '啊啊啊啊啊啊啊';
	$post_arr['argumentList'] = 'com.qdazzle.x3dgame,android,d//igwEhgBGCI2TG6lWqlK4CSeMgrDWbmRbGKKIKmH+q1XUWVUsz5OJYvdoTZPPQYgIlTPJuSLI755d0r8DKYJWOp+qBsCy8S2Me0kKcp7w=||com.qdazzle.x3dgame,android,d//igwEhgBGCI2TG6lWqlK4CSeMgrDWbmRbGKKIKmH/awRG97IlZ4FoUmEL4nYjGo+t4PqjK4daS++rggZXE4cGKu1FH5FgAG7nvF30FvA4=';
	
	$curl = curl_init($url);
	$timeout = 30;
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
	//curl_setopt($curl, CURLOPT_HTTPHEADER, array("Content-Type: multipart/form-data"));
	curl_setopt($curl, CURLOPT_POST, 1);
	curl_setopt($curl, CURLOPT_POSTFIELDS, $post_arr);
	curl_setopt($curl, CURLOPT_TIMEOUT, $timeout);
	$content = curl_exec($curl);
	$http_code = curl_getinfo($curl,CURLINFO_HTTP_CODE);
	curl_close($curl);
	print_r($content);


