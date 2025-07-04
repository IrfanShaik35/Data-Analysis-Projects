
use project2

select * from raw_orders


--3. checking for duplicate rows 
select order_id,count(order_id) from raw_orders
group by order_id
--(no duplicate rows to remove)


--4. updating same readable id in customer_id of orders with help of customers table (to maintain relationship)
update raw_orders
set customer_id = (select c.cust_id from raw_customers c
				where raw_orders.customer_id=c.customer_id)


--7. changing data type of customer_id with int and foreign key 
alter table raw_orders 
alter column customer_id int

alter table raw_orders 
add constraint FK_customer_id foreign key(customer_id) references raw_customers(customer_id)


--12. making orderid readable .(generating orderid based on oldest orderdate to new(real world scenario) which wont effect data ) and changing its datatype to int primary
with cte as(
select order_id,order_date, row_number() over(order by order_date) as oid from raw_orders)

update raw_orders
set order_id = (select c.oid from cte c
				where raw_orders.order_id=c.order_id)

alter table raw_orders 
alter column order_id int not null

alter table raw_orders 
add constraint PK_order_id primary key(order_id)


--13. changing data type of order amount to numeric(decimal) from float since it ensures the accuracy and integrity of your monetary data in a database.
alter table raw_orders 
alter column order_amount decimal(10,2)


--14. Handling nulls in order amount ( if we have nulls in price or amount then simply it mean 0 .if we wont handle null it reflect in calculation like avg
--(5+6)/2 rather than (5+6+0)/3)
update raw_orders
set order_amount=coalesce(order_amount,0)
where order_amount is null


--15. order_date is good (no nulls,missing values,in date formate only )

--16. formating status col and handling nulls(which converted into missing values after formating)
update raw_orders
set status= trim(concat(upper(left(status,1)),lower(substring(status,2,len(status)))))

update raw_orders
set status='N/A'
where status=' '







