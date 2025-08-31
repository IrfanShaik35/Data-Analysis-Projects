
-- creating DB
create database delivery_apps

use delivery_apps

select * from food_Data

--1. cleaning data

--deleting unnecessary columns
alter table food_Data
drop column Location,[Product category],Promo,[Price per Gm],[price per 100g],[weight(g).1],[mrp.1],[promo.1],[selling price.1],[sattviko price per gm],[Difference (per gm)],[Difference (per 100 gm)],[remarks]

--deleting null values
delete from food_Data
where [Product Name] is null and brand is null and [weight(g)] is null and mrp is null and [sattviko price per 100gm] is null 

delete from food_Data
where [Product Name] is null 

delete from food_Data
where  brand is null and [weight(g)] is null and mrp is null and [sattviko price per 100gm] is null 

update food_Data
set [Weight(g)]=50
where [Weight(g)] is null and [Product Name]='MTR Masala Upma Mix'

update food_Data
set MRP=100
where MRP is null and [Product Name]='MTR Masala Upma Mix'

update food_Data
set [Selling Price]=100
where [Selling Price] is null and [Product Name]='MTR Masala Upma Mix'


delete from food_Data
where  brand is null 

--lowercasing values
update food_Data
set [Product Name]= lower([Product Name])

update food_Data
set Brand= lower(Brand)

update food_Data
set [Product Name]=replace([Product Name],'piri','peri')

create view cleaned_food_data as
with cte as(
	select [Platform],[product name] as product_name, Brand,
		round(coalesce([Weight(g)],avg([Weight(g)]) over(partition by [product name],platform)),2) as 'Weight(g)' ,
		round(coalesce(mrp,avg(mrp) over(partition by [product name],platform)),2) as 'MRP',
		round(coalesce([selling price],avg([selling price]) over(partition by [product name],platform)),2) as 'Selling_price' ,
		round(coalesce([sattviko price per 100gm],avg([sattviko price per 100gm]) over(partition by [product name],platform)),2) as 'sattviko_price_per_100gm'
from food_Data),


--delete from cte
--where [Weight(g)] is null and MRP is null and selling_price is null and (sattviko_price_per_100gm is null or sattviko_price_per_100gm=0)


 -- calucating price per 100 g and discount
 cte2 as(
	select [Platform],product_name,Brand,[Weight(g)],MRP,Selling_price,
	round(selling_price/([weight(g)]/100),2) as Price_per_100g,
	round(((mrp-selling_price)/mrp)*100,2) as 'discount%',
	coalesce(sattviko_price_per_100gm,0) as sattviko_price_per_100gm
from cte)

select * from cte2

select * from cleaned_food_data
