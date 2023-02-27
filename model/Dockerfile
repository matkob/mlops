FROM 3.10-buster

ARG UNAME=testuser
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME

USER $UNAME

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD /bin/bash