$('#likes').click(function(){


    var catid;
    catid = $(this).attr("data-catid");
    $.get('/rango/like_category/', {category_id: catid}, function(data){
               $('#like_count').html(data);
               $('#likes').hide();
    });
});

$('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
         $('#cats').html(data);
        });
})

$('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
         $('#cats').html(data);
        });
})


$('.rango-add').click(function(){
    var catId;
    var catUrl;
    var catTitle;
    var me = $(this); //
    catId=$(this).attr("data-catid");
    catUrl=$(this).attr("data-url");
    catTitle=$(this).attr("data-title");
    cont_dic={category_id: catId, title: catTitle, url: catUrl};
    $.get('/rango/auto_add_page/',cont_dic, function(data){
    $('#page').html(data);
    me.hide();
    })
})
