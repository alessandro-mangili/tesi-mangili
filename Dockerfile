FROM klee/klee:latest

WORKDIR /workspace

FROM remnux/retdec:latest AS retdec-stage

FROM klee/klee:latest

WORKDIR /workspace

USER root

COPY --from=retdec-stage /usr/local/bin /usr/local/bin
COPY --from=retdec-stage /usr/local/share/retdec /usr/local/share/retdec

RUN chown -R klee:klee /workspace
RUN chmod -R 777 /workspace
USER klee

RUN pip3 install --user --no-cache-dir tabulate

RUN pip3 install --user --no-cache-dir \
    angr \
    claripy \
    pyvex \
    cle \
    archinfo \
    capstone

ENV PATH="/home/klee/.local/bin:${PATH}"


RUN echo 'export PS1="\[\e[1;32m\][analysis]\[\e[0m\] \[\e[1;34m\]\w\[\e[0m\] $ "' >> /home/klee/.bashrc

CMD ["bash"]