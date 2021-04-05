CREATE DATABASE IF NOT EXISTS ecommerce;
CREATE USER IF NOT EXISTS 'ecommerce'@'%' IDENTIFIED BY 'ecommerce';
GRANT ALL PRIVILEGES ON ecommerce.* TO 'ecommerce'@'%';