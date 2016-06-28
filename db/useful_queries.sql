-- to count number of labeled images
select count(*) from images where labeled=true;

-- to count number of labeled images not including crowd
select count(*) from images where labeled=true and set_type!='crowd';

-- to count number of positive patches
select count(*) from labels where type='pos';

-- to count number of positive patches
select count(*) from labels where type='neg';

-- count labels by camera
select camera, count(*) from labels left join images on labels.image=images.id group by images.camera;

-- count positive labels by camera
select camera, count(*) from labels left join images on labels.image=images.id where labels.type='pos' group by images.camera;

-- count negative labels by camera
select camera, count(*) from labels left join images on labels.image=images.id where labels.type='neg' group by images.camera;

-- select heights and widths of positive labels
select (boty-topy) as height, (botx-topx) as width from labels where type='pos';

-- select heights and widths of negative labels
select (boty-topy) as height, (botx-topx) as width from labels where type='neg';
