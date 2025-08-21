FROM odoo:17
LABEL MAINTAINER="Francesca MBOUEMBE <francescambouembe@gmail.com>"
RUN pip3 install xlsxwriter \
    && pip3 install xlrd \
    && pip3 install openpyxl
COPY ./modules /mnt/extra-addons/