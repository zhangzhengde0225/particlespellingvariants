


python -m ParSV.worker.psv_remote_model \
    --host 0.0.0.0 \
    --port None \
    --permissions "users: admin; groups: payg; owner:zdzhang@ihep.ac.cn" \
    --author zhangbolun@ihep.ac.cn \
    --controller_address https://aiapi.ihep.ac.cn \
    --no_register False \
    $@
