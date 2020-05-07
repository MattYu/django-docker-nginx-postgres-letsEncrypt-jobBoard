FROM linuxserver/letsencrypt

RUN rm /config/nginx/site-confs/default

COPY sites-enabled/ /config/nginx/site-confs
COPY config/ssl.conf /config/nginx/ssl.conf

