
use project2


select * from raw_customers


--1. checking for duplicate rows
select customer_id,count(customer_id) from raw_customers
group by customer_id
--(no duplicate rows to remove)

--2. adding temporay readable customer id column 
alter table raw_customers
add cust_id int identity(1,1)

--5. deleting temp cust_id col by updating its value with customer_id
update raw_customers
set customer_id=cust_id

alter table raw_customers
drop column cust_id

--6. changing data type of customer_id with int and primary key (column should be not null to be a primary)
alter table raw_customers 
alter column customer_id int not null

alter table raw_customers 
add constraint PK_customer_id primary key (customer_id)  

--8. removing any whitespaces in name, email and state, formating name and state into 1 format, formating email
update raw_customers
set name=trim(name), email=trim(email),state=trim(state)

update raw_customers
set name=concat(upper(left(name,1)),lower(substring(name,2,len(name)))),
state=concat(upper(left(state,1)),lower(substring(state,2,len(state))))

--(in email few are like 'kevin33 at gmail.com' rather than 'kevin33@gmail.com ' formating them
update raw_customers
set email=replace(email,' at ','@')
where email not like '%@%'

--9. foramting phone no. (len should be 10) 
update raw_customers
set phone = replace(replace(replace(replace(replace(phone,'+1' ,''),'.',''),'(',''),')',''),'-','') 

--(removing no. that start with 001)
update raw_customers
set phone =replace(phone,'001','')
where phone like '001%'

--(atlast we remove no. that ending like x6589)
update raw_customers
set phone=replace(phone,substring(phone,11,len(phone)),'')


--10. Handling missing values  (state has missing values which cannot replace with any other values as it may result in our analysis so replaacing those with N/A)
update raw_customers
set state='N/A'
where state =' '

--11.signup_date col already in date type so no changes