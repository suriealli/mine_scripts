/**************
	@js页面开始加载
	@CopyRight teamtop
	@author alven wang
	@email 605470805@qq.com
	@2012-02
***************/
$(document).ready(function() {
	$("#myTable").tablesorter({
	sortList: [[0,0]],
	widgets: ['zebra']
	});
	$("#myTable tbody tr").hover(function() {
		// $("#orderedlist li:last").hover(function() {
			$(this).addClass("blue");
		}, function() {
			$(this).removeClass("blue");
		});
	});