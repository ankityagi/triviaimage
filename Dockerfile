# Use official PHP image with SQLite extension
FROM php:8.2-apache

# Enable mod_rewrite for pretty URLs (optional)
RUN a2enmod rewrite



# Copy everything into Apache document root
COPY . /var/www/html/


# Ensure permissions for database
RUN chown -R www-data:www-data /var/www/html/database

# Expose port 80
EXPOSE 80


# Set working directory
WORKDIR /var/www/html

# Set recommended PHP settings for SQLite
RUN echo "upload_max_filesize = 20M\npost_max_size = 20M" > /usr/local/etc/php/conf.d/uploads.ini


RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

RUN echo "DirectoryIndex index.php" >> /etc/apache2/apache2.conf


# Healthcheck (optional)
HEALTHCHECK CMD curl --fail http://localhost/ || exit 1
