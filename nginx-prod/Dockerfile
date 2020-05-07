FROM linuxserver/letsencrypt

RUN rm /config/nginx/site-confs/default
RUN rm -r /config/.

COPY config/ /config
COPY config/nginx.conf /config/nginx/site-confs/default
COPY config/ssl.conf /config/nginx/ssl.conf

