;(function(){
	var $bregist = document.getElementById("regist");
	var $bvhod = document.getElementById("vhod");
		
	document.getElementById("regist").remove();
		
	document.getElementById("reg").onclick = function(){
		//var $bvhod = document.getElementById("vhod");
		document.getElementById("vhod").remove();
		document.getElementById("osn").append($bregist);
		
		document.getElementById("reg").style.display = "none";
		document.getElementById("vh").style.display = "";
	};
	
	
	document.getElementById("vh").onclick = function(){
		//var $bregist = document.getElementById("regist");
		document.getElementById("regist").remove();
		document.getElementById("osn").append($bvhod);
		
		document.getElementById("vh").style.display = "none";
		document.getElementById("reg").style.display = "";
	};
})();