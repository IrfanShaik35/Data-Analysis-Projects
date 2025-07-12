

use project3

--establishing relation 
alter table orders
add constraint FK_Customer_ID foreign key(Customer_ID) references customers(Customer_id)

alter table orders
add constraint FK_Book_ID foreign key(Book_ID) references Books(Book_id)


--exploring tables
select * from Books
select * from Customers
select * from orders

--1) Top 5 books by revenue
--(explaination: need to find total revenue of each book among them we need top 5 books)
select top 5 * from (
	select b.Book_ID,b.title,b.Author,b.genre,sum(o.Total_Amount) as total_revenue from books b
	left join orders o
	on b.Book_ID=o.book_id
	group by b.Book_ID,b.title,b.Author,b.genre)t
order by total_revenue desc


--2) Average order value by customer nationality
--(explaination: calculate the average amount customers from each country spend on their orders.)
select c.country,round(avg(o.total_amount),2) as avg_amount from Customers c
left join orders o
on c.Customer_ID=o.Customer_ID
group by c.country
order by avg_amount desc


--3) List customers who have ordered atleast 4 different genres
select customer_id,name from(
		select c.customer_id,c.name,count(distinct b.genre) unique_genre_ordered from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
		group by c.customer_id,c.name
		having  count(distinct b.genre)>=4)t
order by unique_genre_ordered desc


--4) Books never ordered 
select b.book_id,b.Title,b.author,b.genre from books b
left join orders o
on b.Book_ID=o.Book_ID
where o.Book_ID is null
order by b.book_id


--5) Customers with the most variety in genres
--(explaination: similar to ques3 but here finding all ie. List customers who have ordered different genres  )
select customer_id,name from(
		select c.customer_id,c.name,count(distinct b.genre) unique_genre_ordered from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
		group by c.customer_id,c.name)t
order by unique_genre_ordered desc


--6) Top 2 highest-spending customers per country
--(explaination:  choosing top 2 customer who spend highest for each country )
with cte as (select *,rank() over(partition by country order by total_spending desc) as rank_of_highest_spending_of_each_country from(
		select  c.customer_id,c.name,c.country,sum(o.total_amount) as total_spending
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		group by c.customer_id,c.name,c.country )t)

select customer_id,name,country,total_spending from cte
where rank_of_highest_spending_of_each_country<=2


--7) Book with highest order quantity per month
with cte as(select *,max(quantity) over(partition by year,month) as highest_quantity from(
	select b.book_id,b.title,b.author,o.quantity,year(o.order_date) as year,month(o.order_date) as month
	from books b
	join orders o
	on b.Book_ID=o.Book_ID)t)

select year,month,book_id,title,author,quantity from cte
where quantity=highest_quantity


--8) Customer’s lifetime value vs. average LTV in their country
--(explaination: For every customer, calculate their total spending and compare it with the average spending of other customers of same country)
with cte as(select  c.customer_id,c.name,c.country,sum(o.total_amount) as total_spending
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		group by c.customer_id,c.name,c.country)

select *, round(avg(total_spending) over(partition by country),2) as avg_lifetime_value_of_country,
case when total_spending <avg(total_spending) over(partition by country) then 'below the avg of LTV of country'
     when total_spending >avg(total_spending) over(partition by country) then 'above the avg of LTV of country' 
	 else 'constant'
end as 'LTV of customer'
from cte


--9) Genre trends over time
--(explaination: Show how the popularity of each genre has changed month by month based on total quantity ordered.)
with cte1 as (
	select *,count(*) over(partition by year_month) no_of_genres from
		(select format(o.order_date,'yyyy-MM') as year_month,b.Genre,sum(o.quantity) total_quantity from books b
		join orders o
		on b.Book_ID=o.Book_ID
		group by format(o.order_date,'yyyy-MM'),b.Genre)t
	),

cte2 as(select year_month,genre,total_quantity,
		lag(year_month,no_of_genres) over(order by year_month) as prev_month from cte1)

select c1.genre,c1.year_month as current_month,c1.total_quantity as current_month_total_quantity,
c1.prev_month,c2.total_quantity as prev_month_total_quantity,
case when c1.total_quantity>c2.total_quantity then 'quantity increases than previous month'
     when c1.total_quantity<c2.total_quantity then 'quantity decreses than previous month' 
	 when c2.total_quantity is null then 'no previous month data'
	 else 'constant'
end as trends
from cte2 c1
left join cte2 c2
on c1.genre=c2.genre and c1.prev_month=c2.year_month 
order by c1.year_month,c1.genre


--10) Author with most consistent monthly sales
--(explaination: Determine which author has the most consistent monthly sales — i.e., minimal variation in order quantities across months(ordered months for each author).
-- we use varinace var() in monthly sales per author and The author with the lowest variation across months would be the most consistent

with cte1 as(select b.author,o.order_date,sum(o.Quantity) as quantity_sold
from books b
		left join orders o
		on b.Book_ID=o.Book_ID
		group by b.author,o.order_date
		having o.order_date is not null),

cte2 as(select author,var(quantity_sold)  as varience,
        case when var(quantity_sold)=0 then 'consistent'
		else 'inconsistent'
		end as consistency
		from cte1
		group by author
		having var(quantity_sold) is not null)

select author from cte2
where consistency='consistent'



--11) Top selling book in the last 8 months
--(explaination: Find the top-selling book (by quantity) within the last 8 months)
with cte1 as (
    select * 
    from orders
    where datediff(month, order_date, getdate()) <= 8
),
cte2 as (
    select 
        b.book_id,
        b.title,
        b.author,
        b.genre,
        sum(c.quantity) as total_quantity
    from cte1 c
    join books b on b.book_id = c.book_id
    group by b.book_id, b.title, b.author, b.genre
),
cte3 as (
    select *,
           rank() over(order by total_quantity desc) as rnk
    from cte2
)
select book_id, title, author, genre, total_quantity
from cte3
where rnk = 1




--12) Longest gap between two orders for each customer
--(explaination: For each customer, find the longest time gap between two consecutive orders.)
with cte as(
		select  c.Customer_ID,c.Name,o.order_date,
		lead(o.order_date) over(partition by c.customer_id order by o.order_date) nxt_order_date,
		datediff(day,o.order_date,lead(o.order_date) over(partition by c.customer_id order by o.order_date)) diff_order_date
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID)

select Customer_ID,Name,Order_Date,nxt_order_date,longest_time_gap_in_days from (
		select *,
		max(diff_order_date) over(partition by customer_id,name) as longest_time_gap_in_days from cte)t
where diff_order_date=longest_time_gap_in_days


		
--13) Restock suggestion: Books with stock < average order quantity
--(explaination: Suggest books that might need restocking because their average demand (based on order quantities) is higher than the current stock available.)
select distinct b.book_id,b.title,b.author,b.genre,b.stock,
avg(o.quantity) over(partition by b.title order by b.book_id) avg_quantity,
case when avg(o.quantity) over(partition by b.title)>b.stock then 'need restocking'
     else 'no need restocking'
end restock_suggestion
from books b
		join orders o
		on b.Book_ID=o.Book_ID
order by restock_suggestion


--14) Customers who ordered books older than 50 years
select c.Customer_ID,c.name,b.title,b.author,b.published_year,
		year(getdate())-b.Published_Year as book_age  from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
where year(getdate())-b.Published_Year>50


--15) Order-to-stock ratio per book
--(explaination: For each book, calculate how many units were sold compared to how many are currently in stock — the order-to-stock ratio.)
with cte as(
		select b.book_id,b.title,b.author,b.genre,b.stock,sum(o.quantity) as total_quantity_sold from books b
		join orders o
		on b.Book_ID=o.Book_ID
		group by b.book_id,b.title,b.author,b.genre,b.stock)

select *,
case when stock=0 then 999
     else round(cast(total_quantity_sold as float)/stock,2)
end ratio,
case when stock=0 or round(cast(total_quantity_sold as float)/stock,2)>=1 then 'low'
     when round(cast(total_quantity_sold as float)/stock,2)<1 then 'high'
end OTS_ratio
	 from cte
order by ratio desc


--16) Customers who have only ever ordered a single book, but ordered it more than once
--(explaination: Bought only one distinct book title, and Ordered that book more than once (quantity > 1))
with cte as(select c.customer_id,c.Name,b.title,sum(o.quantity) total_quantity from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
		group by c.customer_id,c.Name,b.title
		having sum(o.quantity)=1)

select c.customer_id,c.Name,b.title,count(*) total_quantity from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
		group by c.customer_id,c.Name,b.title
		having count(*)>1 and c.Customer_ID not in (select customer_id from cte)


--17) Rising Reader Trend
--(explaination: Identify customers whose total number of books ordered has increased consistently over the last 3 months.)
with cte as(
	select c.Customer_ID,
	c.Name,o.order_date,o.Quantity,
	case when lag(o.quantity) over(partition by c.name order by order_date)<o.quantity and
			  lag(o.quantity,2) over(partition by c.name order by order_date)<o.quantity 
			  and lag(o.quantity) over(partition by c.name order by order_date)> lag(o.quantity,2) over(partition by c.name order by order_date)
			  then 'consistent'
		else 'inconsistent'
	end reader_trend
	from customers c
	join orders o
	on c.Customer_ID=o.Customer_ID)

select customer_id,name from cte
where reader_trend='consistent'



--18) High-Spike Buying Behavior
--(explaination: Find customers who placed 80% or more of their total lifetime order value within a single week.)

--total lifetime spending
with cte as(select  c.customer_id,c.name,sum(o.total_amount) as total_spending
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		group by c.customer_id,c.name)

--calculating total spending of that week of year and among them choosing which are >= total lifetime spending		
select  c.customer_id,c.name,year(o.order_date) year,datepart(WK,o.Order_Date) week,ct.total_spending ,sum(o.total_amount) as total_spending_weekly
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		join cte ct
		on c.Customer_ID=ct.Customer_ID
		group by c.customer_id,c.name,year(o.order_date),datepart(WK,o.Order_Date),total_spending
		having sum(o.total_amount)>=0.8*ct.total_spending
		



--19) Weekend-Only Book Buyers
--(explaination: List customers who only place orders on weekends (Saturday/Sunday) over their entire order history)
with cte as(
		select c.Customer_ID,c.Name,o.order_date,datename(dw,o.order_date) days
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		where datename(dw,o.order_date)!='Saturday' and datename(dw,o.order_date)!='Sunday')

select c.Customer_ID,c.Name,o.order_date,datename(dw,o.order_date)
		from customers c
		join orders o
		on c.Customer_ID=o.Customer_ID
		where c.Customer_ID not in (select Customer_ID from cte)
		order by c.customer_id
		
		


--20) Genre Loyalty Index
--(explaination: For each customer, calculate a loyalty score for every genre they’ve purchased from — 
--defined as the percentage of their total orders that belong to their most frequently ordered genre. Return customers whose loyalty score is over 80%)
with cte1 as(
		select c.customer_id,c.Name,sum(o.quantity) total_quantity from orders o
		join Customers c
		on o.Customer_ID=c.Customer_ID
		group by c.customer_id,c.Name),

cte2 as	(select c.customer_id,c.Name,b.genre,ct.total_quantity,sum(o.quantity) total_quantity_each_genre,
		round(cast(sum(o.quantity) as float)/ct.total_quantity*100,2) as loyalty_score
		from orders o
		join books b
		on o.Book_ID=b.Book_ID
		join Customers c
		on o.Customer_ID=c.Customer_ID
		join cte1 ct
		on o.customer_id=ct.customer_id
		group by c.customer_id,c.Name,b.genre,ct.total_quantity)

select * from cte2
where loyalty_score>80
order by name

