server {
    listen 80;
    server_name "%(DNS_SUB_DOMAIN)s.%(DNS_DOMAIN)s";
    root /data/www/%(PROJECT_NAME)s;

    location ~* ^/.+\.(jpg|css|jpeg|gif|png|css|zip) {
    access_log   off; #
    expires      30d; 
    }

    location / {
        # host and port to fastcgi server
        fastcgi_pass 127.0.0.1:%(WEB_SERVER_FASTCGI_PORT)s;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param REQUEST_METHOD $request_method;
        fastcgi_param QUERY_STRING $query_string;
        fastcgi_param CONTENT_TYPE $content_type;
        fastcgi_param CONTENT_LENGTH $content_length;
        fastcgi_param SERVER_PORT $server_port;
        fastcgi_param SERVER_PROTOCOL $server_protocol;
        fastcgi_param SERVER_NAME $server_name;
        fastcgi_pass_header Authorization;
        fastcgi_intercept_errors off;
    }

    #access_log     /var/log/nginx/localhost.access_log main;
    #error_log      /var/log/nginx/localhost.error_log;

    location ^~ /media/ {
        root    /data/www/%(PROJECT_NAME)s/;
        #autoindex on;
    }

}
