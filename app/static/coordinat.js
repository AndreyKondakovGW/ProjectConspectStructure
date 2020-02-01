function preview(img, selection) {
    var scaleX = 100 / (selection.width || 1);
    var scaleY = 100 / (selection.height || 1);
    $('#photo + div > img').css({
        width: Math.round(scaleX * 600) + 'px',
        height: Math.round(scaleY * 400) + 'px',
        marginLeft: '-' + Math.round(scaleX * selection.x1) + 'px',
        marginTop: '-' + Math.round(scaleY * selection.y1) + 'px'
    });
} 

$(document).ready(function () {
    $('#photo').imgAreaSelect({
       // aspectRatio: '1:1',
        handles: true,
        onSelectChange: preview,
        onSelectEnd: function ( image, selection ) {
            $('input[name=x1]').val(selection.x1);
            $('input[name=y1]').val(selection.y1);
            $('input[name=x2]').val(selection.x2);
            $('input[name=y2]').val(selection.y2);
            $('input[name=w]').val(selection.width);
            $('input[name=h]').val(selection.height);
        }
    });
}); 