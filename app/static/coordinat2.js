
;(function(){
	console.log("ширина картинки=",document.getElementById("photo").offsetWidth);
	console.log("высота картинки=",document.getElementById("photo").offsetHeight);
	$('input[name=w]').val(document.getElementById("photo").offsetWidth);
    $('input[name=h]').val(document.getElementById("photo").offsetHeight);
})();

function preview(img, selection) {} 

$(document).ready(function () {
    $('#photo').imgAreaSelect({
        handles: true,
        onSelectChange: preview,
        onSelectEnd: function ( image, selection ) {
			//левый верхний угол
            $('input[name=x1]').val(selection.x1);
            $('input[name=y1]').val(selection.y1);
			//правый нижний угол
            $('input[name=x2]').val(selection.x2);
            $('input[name=y2]').val(selection.y2);
			
			//выведение данных в консоль
			console.log("x1=",selection.x1);
			console.log("y1=",selection.y1);
			console.log("x2=",selection.x2);
			console.log("y2=",selection.y2);
			console.log("ширина=",selection.width);
			console.log("высота=",selection.height);
        }
    });
}); 

