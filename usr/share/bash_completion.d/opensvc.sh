

svcmgr="abort boot clear collector compliance create delete deploy disable dns docker edit enable eval freeze frozen get giveback install logs ls migrate monitor move pg podman postsync presync print provision prstatus pull purge push resource restart resync run scale set shutdown snooze start startstandby status stop support switch sync takeover thaw toc unprovision unset unsnooze update validate"
svcmgr_collector="ack alerts asset checks create disks events list log networks show tag untag"
svcmgr_collector_ack="action unavailability"
svcmgr_collector_create="tag"
svcmgr_collector_list="actions tags unavailability"
svcmgr_collector_list_unavailability="ack"
svcmgr_collector_show="actions tags"
svcmgr_compliance="attach auto check detach env fix fixable list show"
svcmgr_compliance_list="moduleset ruleset"
svcmgr_compliance_show="moduleset ruleset status"
svcmgr_dns="update"
svcmgr_edit="config"
svcmgr_install="secrets"
svcmgr_pg="freeze kill thaw"
svcmgr_print="base config devs exposed resinfo resource schedule status sub"
svcmgr_print_base="devs"
svcmgr_print_config="mtime"
svcmgr_print_exposed="devs"
svcmgr_print_resource="status"
svcmgr_print_sub="devs"
svcmgr_push="config encap resinfo status"
svcmgr_push_encap="config"
svcmgr_resource="monitor"
svcmgr_set="provisioned unprovisioned"
svcmgr_sync="all break drp establish full nodes quiesce restore resume resync revert split update verify"
svcmgr_validate="config"
svcmgr_set="--add --color --debug --dry-run --env --eval --index --kw --local --master --namespace --node --nolock --param --remove --rid --slave --slaves --status --subsets --tags --value --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_unset="--color --debug --dry-run --env --kw --local --master --namespace --node --nolock --param --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_eval="--color --debug --dry-run --env --format --impersonate --kw --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_get="--color --debug --dry-run --env --eval --format --impersonate --kw --local --master --namespace --node --nolock --param --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_edit_config="--color --debug --discard --env --namespace --recover --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_delete="--color --debug --dry-run --env --interval --local --master --namespace --node --nolock --purge-collector --rid --slave --slaves --stats --status --subsets --tags --time --unprovision --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_validate_config="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_create="--color --config --debug --disable-rollback --dry-run --env --leader --local --master --namespace --node --nolock --provision --resource --restore --rid --slave --slaves --status --subsets --tags --template --waitlock -c --cluster -f --force -h --help -i --interactive -p --parallel -s --service"
svcmgr_print_config="--color --debug --env --eval --filter --format --impersonate --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_update="--color --debug --disable-rollback --dry-run --env --local --master --namespace --node --nolock --provision --resource --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_compliance_fix="--attach --color --debug --env --module --moduleset --namespace --ruleset-date --status --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_compliance_list_moduleset="--color --debug --env --moduleset --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_detach="--color --debug --env --moduleset --namespace --ruleset --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_attach="--color --debug --env --moduleset --namespace --ruleset --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_show_ruleset="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_env="--color --debug --env --module --moduleset --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_show_status="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_list_ruleset="--color --debug --env --namespace --ruleset --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_fixable="--attach --color --debug --env --module --moduleset --namespace --ruleset-date --status --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_compliance_show_moduleset="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_compliance_check="--attach --color --debug --env --module --moduleset --namespace --ruleset-date --status --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_compliance_auto="--attach --color --cron --debug --env --module --moduleset --namespace --ruleset-date --status --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_collector_disks="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_log="--color --debug --env --message --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_networks="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_list_actions="--begin --color --debug --end --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_checks="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_tag="--color --debug --env --namespace --status --tag --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_ack_unavailability="--account --author --begin --color --comment --debug --duration --end --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_list_tags="--color --debug --env --filter --format --like --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_untag="--color --debug --env --namespace --status --tag --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_show_actions="--begin --color --debug --end --env --filter --format --id --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_show_tags="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_list_unavailability_ack="--author --begin --color --comment --debug --end --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_create_tag="--color --debug --env --namespace --status --tag --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_ack_action="--author --color --comment --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_alerts="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_events="--begin --color --debug --end --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_collector_asset="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_sync_update="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_boot="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_push_encap_config="--color --cron --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_move="--color --debug --disable-rollback --env --interval --namespace --stats --status --time --to --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_shutdown="--color --debug --dry-run --env --interval --local --master --namespace --node --nolock --rid --slave --slaves --stats --status --subsets --tags --time --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_push_resinfo="--color --cron --debug --env --namespace --status --sync --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_unsnooze="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_monitor="--color --debug --env --interval --namespace --node --stats --status --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_sync_establish="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_support="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_set_unprovisioned="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_start="--color --debug --disable-rollback --dry-run --env --interval --local --master --namespace --node --nolock --rid --slave --slaves --stats --status --subsets --tags --time --upto --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_ls="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_toc="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_push_status="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_set_provisioned="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_print_status="--color --debug --env --filter --format --hide-disabled --namespace --node --show-disabled --status --waitlock -c --cluster -h --help -p --parallel -r --refresh -s --service"
svcmgr_enable="--color --debug --env --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_thaw="--color --debug --env --interval --local --master --namespace --node --slave --slaves --stats --status --time --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_stop="--color --debug --downto --dry-run --env --interval --local --master --namespace --node --nolock --rid --slave --slaves --stats --status --subsets --tags --time --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_print_exposed_devs="--color --debug --env --filter --format --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_print_resinfo="--color --debug --env --filter --format --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_unprovision="--color --debug --dry-run --env --interval --leader --local --master --namespace --node --nolock --rid --slave --slaves --stats --status --subsets --tags --time --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_print_devs="--color --debug --env --filter --format --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_provision="--color --debug --disable-rollback --dry-run --env --interval --leader --local --master --namespace --node --nolock --rid --slave --slaves --stats --status --subsets --tags --time --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_restart="--color --debug --disable-rollback --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_sync_revert="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_pull="--color --debug --disable-rollback --env --namespace --provision --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_install_secrets="--color --debug --env --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_sync_all="--color --cron --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_frozen="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_sync_quiesce="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_purge="--color --debug --dry-run --env --interval --leader --local --master --namespace --node --nolock --purge-collector --rid --slave --slaves --stats --status --subsets --tags --time --wait --waitlock -c --cluster -f --force -h --help -p --parallel -s --service -w --watch"
svcmgr_sync_nodes="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_abort="--color --debug --env --interval --namespace --stats --status --time --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_print_sub_devs="--color --debug --env --filter --format --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_push_config="--color --cron --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_status="--color --cron --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -r --refresh -s --service"
svcmgr_logs="--backlog --color --debug --env --follow --local --namespace --no-pager --node --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_dns_update="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_migrate="--color --debug --disable-rollback --env --interval --namespace --stats --status --time --to --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_sync_resync="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_freeze="--color --debug --env --interval --local --master --namespace --node --slave --slaves --stats --status --time --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_print_config_mtime="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_resync="--color --debug --disable-rollback --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_pg_freeze="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_scale="--color --debug --env --local --namespace --node --status --to --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_presync="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_sync_split="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_pg_kill="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_giveback="--color --debug --disable-rollback --env --interval --namespace --stats --status --time --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_resource_monitor="--color --cron --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_print_resource_status="--color --debug --env --filter --format --namespace --rid --status --waitlock -c --cluster -h --help -p --parallel -r --refresh -s --service"
svcmgr_sync_break="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_prstatus="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_print_base_devs="--color --debug --env --filter --format --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_sync_full="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_run="--color --cron --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_deploy="--color --config --debug --disable-rollback --dry-run --env --leader --local --master --namespace --node --nolock --restore --rid --slave --slaves --status --subsets --tags --template --waitlock -c --cluster -f --force -h --help -i --interactive -p --parallel -s --service"
svcmgr_pg_thaw="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_sync_restore="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_startstandby="--color --debug --disable-rollback --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_podman="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_takeover="--color --debug --disable-rollback --env --interval --namespace --stats --status --time --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_snooze="--color --debug --duration --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_sync_resume="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_sync_drp="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_clear="--color --debug --env --local --namespace --node --slave --slaves --status --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_postsync="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_sync_verify="--color --debug --dry-run --env --local --master --namespace --node --nolock --rid --slave --slaves --status --subsets --tags --waitlock -c --cluster -f --force -h --help -p --parallel -s --service"
svcmgr_switch="--color --debug --disable-rollback --env --interval --namespace --stats --status --time --to --wait --waitlock -c --cluster -h --help -p --parallel -s --service -w --watch"
svcmgr_disable="--color --debug --env --namespace --rid --status --subsets --tags --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_print_schedule="--color --debug --env --filter --format --namespace --status --verbose --waitlock -c --cluster -h --help -p --parallel -s --service"
svcmgr_docker="--color --debug --env --namespace --status --waitlock -c --cluster -h --help -p --parallel -s --service"
nodemgr="array auto checks collect collector compliance daemon delete dequeue dns edit eval events freeze frozen get logs ls network ping pool print prkey pushasset pushbrocade pushcentera pushdcs pushdisks pushemcvnx pusheva pushfreenas pushgcedisks pushhds pushhp3par pushibmds pushibmsvc pushnecism pushnetapp pushnsr pushpatch pushpkg pushstats pushsym pushvioserver pushxtremio reboot register rotate scanscsi schedule set shutdown snooze stonith sysreport thaw unschedule unset unsnooze updatecomp updatepkg validate wait wol"
nodemgr_auto="reboot"
nodemgr_collect="stats"
nodemgr_collector="ack alerts asset checks cli create disks events list log networks search show tag untag"
nodemgr_collector_ack="action"
nodemgr_collector_create="tag"
nodemgr_collector_list="actions filtersets nodes services tags"
nodemgr_collector_show="actions tags"
nodemgr_compliance="attach auto check detach env fix fixable list show"
nodemgr_compliance_list="module moduleset ruleset"
nodemgr_compliance_show="moduleset ruleset status"
nodemgr_daemon="blacklist join leave lock rejoin relay restart running shutdown start stats status stop"
nodemgr_daemon_blacklist="clear status"
nodemgr_daemon_lock="release"
nodemgr_daemon_relay="status"
nodemgr_dequeue="actions"
nodemgr_dns="dump"
nodemgr_edit="authconfig config"
nodemgr_network="ls setup show status"
nodemgr_pool="create ls status"
nodemgr_pool_create="volume"
nodemgr_print="authconfig config devs schedule"
nodemgr_rotate="root"
nodemgr_rotate_root="pw"
nodemgr_schedule="reboot"
nodemgr_schedule_reboot="status"
nodemgr_unschedule="reboot"
nodemgr_validate="config"
nodemgr_compliance_fix="--attach --color --debug --filter --force --format --module --moduleset --ruleset-date -h --help"
nodemgr_compliance_list_moduleset="--color --debug --filter --format --moduleset -h --help"
nodemgr_compliance_detach="--color --debug --filter --format --moduleset --ruleset -h --help"
nodemgr_compliance_attach="--color --debug --filter --format --moduleset --ruleset -h --help"
nodemgr_compliance_show_ruleset="--color --debug --filter --format -h --help"
nodemgr_compliance_env="--color --debug --filter --format --module --moduleset -h --help"
nodemgr_compliance_show_status="--color --debug --filter --format -h --help"
nodemgr_compliance_list_ruleset="--color --debug --filter --format --ruleset -h --help"
nodemgr_compliance_fixable="--attach --color --debug --filter --force --format --module --moduleset --ruleset-date -h --help"
nodemgr_compliance_list_module="--color --debug --filter --format -h --help"
nodemgr_compliance_show_moduleset="--color --debug --filter --format -h --help"
nodemgr_compliance_check="--attach --color --debug --filter --force --format --module --moduleset --ruleset-date -h --help"
nodemgr_compliance_auto="--color --cron --debug --filter --format -h --help"
nodemgr_prkey="--color --debug --filter --format -h --help"
nodemgr_pushnsr="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushcentera="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushibmds="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushhp3par="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushxtremio="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushpatch="--color --cron --debug --filter --format -h --help"
nodemgr_pushpkg="--color --cron --debug --filter --format -h --help"
nodemgr_pushvioserver="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushasset="--color --cron --debug --filter --format --sync -h --help"
nodemgr_pushibmsvc="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushnetapp="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushgcedisks="--color --cron --debug --filter --format --object -h --help"
nodemgr_pusheva="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushnecism="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushdcs="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushbrocade="--color --cron --debug --filter --format --object -h --help"
nodemgr_sysreport="--color --cron --debug --filter --force --format -h --help"
nodemgr_pushemcvnx="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushfreenas="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushhds="--color --cron --debug --filter --format --object -h --help"
nodemgr_pushstats="--begin --color --cron --debug --end --filter --format --stats-dir -h --help"
nodemgr_pushsym="--color --cron --debug --filter --format --object --symcli-db-file -h --help"
nodemgr_checks="--color --cron --debug --filter --format -h --help"
nodemgr_pushdisks="--color --cron --debug --filter --format -h --help"
nodemgr_pool_create_volume="--access --color --debug --filter --format --name --namespace --node --pool --shared --size -h --help"
nodemgr_pool_ls="--color --debug --filter --format -h --help"
nodemgr_pool_status="--color --debug --filter --format --pool -h --help"
nodemgr_set="--add --color --debug --eval --filter --format --index --kw --param --remove --value -h --help"
nodemgr_get="--color --debug --eval --filter --format --impersonate --kw --param -h --help"
nodemgr_validate_config="--color --debug --filter --format -h --help"
nodemgr_eval="--color --debug --filter --format --impersonate --kw -h --help"
nodemgr_edit_config="--color --debug --discard --filter --format --recover -h --help"
nodemgr_edit_authconfig="--color --debug --filter --format -h --help"
nodemgr_print_config="--color --debug --filter --format -h --help"
nodemgr_register="--app --color --debug --filter --format --password --user -h --help"
nodemgr_print_authconfig="--color --debug --filter --format -h --help"
nodemgr_unset="--color --debug --filter --format --kw --param -h --help"
nodemgr_delete="--color --debug --filter --format --kw -h --help"
nodemgr_logs="--backlog --color --debug --filter --follow --format --local --node -h --help"
nodemgr_auto_reboot="--color --cron --debug --filter --format -h --help"
nodemgr_freeze="--cluster --color --debug --filter --format --local --node --time --wait -h --help"
nodemgr_schedule_reboot="--color --debug --filter --format -h --help"
nodemgr_shutdown="--cluster --color --debug --filter --format --local --node -h --help"
nodemgr_array="--color --debug --filter --format -h --help"
nodemgr_scanscsi="--color --debug --filter --format --hba --lun --target -h --help"
nodemgr_unsnooze="--color --debug --filter --format -h --help"
nodemgr_unschedule_reboot="--color --debug --filter --format -h --help"
nodemgr_ping="--cluster --color --debug --filter --format --node -h --help"
nodemgr_reboot="--cluster --color --debug --filter --format --local --node -h --help"
nodemgr_wol="--broadcast --color --debug --filter --format --mac --port -h --help"
nodemgr_collect_stats="--color --cron --debug --filter --format -h --help"
nodemgr_ls="--color --debug --filter --format --node -h --help"
nodemgr_events="--color --debug --filter --format --local --node -h --help"
nodemgr_thaw="--cluster --color --debug --filter --format --local --node --time --wait -h --help"
nodemgr_schedule_reboot_status="--color --debug --filter --format -h --help"
nodemgr_print_devs="--color --debug --dev --filter --format --reverse --verbose -h --help"
nodemgr_dequeue_actions="--color --cron --debug --filter --format -h --help"
nodemgr_snooze="--color --debug --duration --filter --format -h --help"
nodemgr_wait="--color --debug --duration --filter --format --local --node -h --help"
nodemgr_updatepkg="--cluster --color --debug --filter --format --local --node -h --help"
nodemgr_frozen="--color --debug --filter --format -h --help"
nodemgr_stonith="--color --debug --filter --format --node -h --help"
nodemgr_rotate_root_pw="--color --cron --debug --filter --format -h --help"
nodemgr_updatecomp="--cluster --color --debug --filter --format --local --node -h --help"
nodemgr_print_schedule="--color --debug --filter --format --verbose -h --help"
nodemgr_daemon_join="--color --debug --filter --format --node --secret -h --help"
nodemgr_daemon_blacklist_clear="--color --debug --filter --format -h --help"
nodemgr_dns_dump="--color --debug --filter --format -h --help"
nodemgr_daemon_restart="--color --debug --filter --format -h --help"
nodemgr_daemon_relay_status="--color --debug --filter --format --node -h --help"
nodemgr_daemon_start="--cluster --color --debug --filter --format --local --node --thread-id -h --help"
nodemgr_daemon_shutdown="--color --debug --filter --format -h --help"
nodemgr_daemon_stats="--color --debug --filter --format --node -h --help"
nodemgr_daemon_stop="--cluster --color --debug --filter --format --local --node --thread-id -h --help"
nodemgr_daemon_running="--color --debug --filter --format -h --help"
nodemgr_daemon_status="--color --debug --filter --format --node -h --help"
nodemgr_daemon_leave="--color --debug --filter --format -h --help"
nodemgr_daemon_rejoin="--color --debug --filter --format --node -h --help"
nodemgr_daemon_blacklist_status="--color --debug --filter --format -h --help"
nodemgr_daemon_lock_release="--color --debug --filter --format --id --name -h --help"
nodemgr_network_setup="--color --debug --filter --format -h --help"
nodemgr_network_ls="--color --debug --filter --format -h --help"
nodemgr_network_show="--color --debug --filter --format --name -h --help"
nodemgr_network_status="--color --debug --filter --format --name --verbose -h --help"
nodemgr_collector_list_tags="--color --debug --filter --format --like -h --help"
nodemgr_collector_disks="--color --debug --filter --format -h --help"
nodemgr_collector_log="--color --debug --filter --format --message -h --help"
nodemgr_collector_events="--begin --color --debug --end --filter --format -h --help"
nodemgr_collector_search="--color --debug --filter --format --like -h --help"
nodemgr_collector_list_filtersets="--color --debug --filter --format -h --help"
nodemgr_collector_list_actions="--begin --color --debug --end --filter --format -h --help"
nodemgr_collector_cli="--api --color --config --debug --filter --format --insecure --password --refresh-api --save --user -h --help"
nodemgr_collector_tag="--color --debug --filter --format --tag -h --help"
nodemgr_collector_list_services="--color --debug --filter --format -h --help"
nodemgr_collector_networks="--color --debug --filter --format -h --help"
nodemgr_collector_untag="--color --debug --filter --format --tag -h --help"
nodemgr_collector_show_actions="--begin --color --debug --end --filter --format --id -h --help"
nodemgr_collector_checks="--color --debug --filter --format -h --help"
nodemgr_collector_show_tags="--color --debug --filter --format -h --help"
nodemgr_collector_create_tag="--color --debug --filter --format --tag -h --help"
nodemgr_collector_list_nodes="--color --debug --filter --format -h --help"
nodemgr_collector_ack_action="--author --color --comment --debug --filter --format -h --help"
nodemgr_collector_alerts="--color --debug --filter --format -h --help"
nodemgr_collector_asset="--color --debug --filter --format -h --help"

opts_with_arg=( "--access" "--add" "--api" "--app" "--author" "--backlog" "--begin" "--broadcast" "--color" "--comment" "--config" "--dev" "--downto" "--duration" "--end" "--env" "--filter" "--format" "--hba" "--id" "--impersonate" "--index" "--interval" "--kw" "--like" "--lun" "--mac" "--message" "--module" "--moduleset" "--name" "--namespace" "--node" "--object" "--param" "--password" "--pool" "--port" "--remove" "--resource" "--rid" "--ruleset" "--ruleset-date" "--secret" "--service" "--size" "--slave" "--stats-dir" "--status" "--subsets" "--symcli-db-file" "--tag" "--tags" "--target" "--template" "--thread-id" "--time" "--to" "--upto" "--user" "--value" "--waitlock" "-s" )



om="setns getns unsetns node cluster svc vol net pool daemon array"

opt_has_arg()
{
    for option in ${opts_with_arg[@]}
    do
        if [ "$option" == "$1" ]
        then
            return 0
        fi
    done
    return 1
}

_comp_handler() 
{
    local a prev action opts
    COMPREPLY=()
    exe="${COMP_WORDS[0]}"
    COMP_WORDS[0]="${exe##*/}"
    a="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [ $COMP_CWORD -eq 1 -a "${COMP_WORDS[0]}" == "om" ]
    then
        svcs=$(cat /var/lib/opensvc/list.services /opt/opensvc/var/list.services 2>/dev/null)
        COMPREPLY=( $(compgen -W "$om $svcs" -- ${a}) )
        return 0
    fi

    case "${prev}" in
        --color)
            COMPREPLY=( $(compgen -W "yes no" -- ${a}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "csv flat_json json table" -- ${a}) )
            return 0
            ;;
        --service|-s)
            svcs=$(cat /var/lib/opensvc/list.services /opt/opensvc/var/list.services 2>/dev/null)
            COMPREPLY=( $(compgen -W "${svcs}" -- ${a}) )
            return 0
            ;;
        --node)
            nodes=$(cat /var/lib/opensvc/list.nodes /opt/opensvc/var/list.nodes 2>/dev/null)
            COMPREPLY=( $(compgen -W "${nodes}" -- ${a}) )
            return 0
            ;;
        *)
            ;;
    esac

    case "${COMP_WORDS[0]} ${COMP_WORDS[1]} "
    in
        "om node ")
            unset COMP_WORDS[0]
            COMP_WORDS[0]="nodemgr"
            COMP_CWORD=${COMP_CWORD-1}
            ;;
        "om net ")
            COMP_WORDS[0]="nodemgr"
            COMP_WORDS[1]="network"
            ;;
        "om pool ")
            COMP_WORDS[0]="nodemgr"
            ;;
        "om daemon "|"om array ")
            COMP_WORDS[0]="nodemgr"
            ;;
        "om svc "|"om vol ")
            unset COMP_WORDS[0]
            COMP_WORDS[0]="svcmgr"
            COMP_CWORD=${COMP_CWORD-1}
            ;;
        "om getns "|"om setns "|"om unsetns ")
            ;;
        "om  ")
            ;;
        om\ *)
            if [ $COMP_CWORD -ge 2 ]
            then
                COMP_WORDS[0]="svcmgr"
                unset COMP_WORDS[1]
            fi
            ;;
    esac

    action=()
    typeset -i skip=0

    for word in ${COMP_WORDS[@]}
    do
        # prevent "Bad substitution" on action deref
        word=${word//[^abcdefghijklmnopqrstuvwxyz0-9_.]/}
        if [ "${word#-}" != "${word}" ]
        then
            opt_has_arg ${word} && skip=1
        elif [ $skip -eq 1 ]
        then
            skip=0
        else
            action+=(${word})
        fi
    done

    action="${action[@]}"
    action="${action// /_}"
    prev_action=""
    opts=""

    while [ "$action" != "" -a "$opts" == "" -a "$prev_action" != "$action" ]
    do
        opts="${!action}"
        prev_action="$action"
        action=${action%_*}
    done

    extra_opts="${!action}"
    if [ "$a" != "" -a "$opts" != "" ]
    then
        opts="$opts $extra_opts"
    fi

    COMPREPLY=($(compgen -W "${opts}" -- ${a}))

    return 0
}

complete -F _comp_handler svcmgr
complete -F _comp_handler nodemgr
complete -F _comp_handler om
