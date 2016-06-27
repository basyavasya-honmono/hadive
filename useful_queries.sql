-- to count number of labeled images
select count(*) from images where labeled=true;

-- to count number of labeled images not including crowd
select count(*) from images where labeled=true and set_type!='crowd';

-- to count number of positive patches
select count(*) from labels where type='pos';
-- to count number of positive patches
select count(*) from labels where type='pos';
