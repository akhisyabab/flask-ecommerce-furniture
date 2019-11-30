CREATE DATABASE flask_ecommerce_furniture_prod;
CREATE DATABASE flask_ecommerce_furniture_dev;
CREATE DATABASE flask_ecommerce_furniture_test;

--CREATE USER flaskecommercefurnitureuser WITH password 'flaskecommercefurniturepassword';
GRANT ALL PRIVILEGES ON database flask_ecommerce_furniture_dev to flaskecommercefurnitureuser;
ALTER USER flaskecommercefurnitureuser SUPERUSER;
