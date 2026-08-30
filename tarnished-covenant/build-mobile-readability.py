from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

css = r'''
/* --- Phone readability pass: readable at arm's length, not microscope distance --- */
@media (max-width: 600px) {
  .app-shell{padding-left:12px;padding-right:12px}
  .tc-screen{padding-left:2px;padding-right:2px}

  /* General supporting copy */
  .tc-muted,.tc-report-detail,.tc-comp-mod p,.tc-comp-legacy,.tc-contract-note,
  .tc-settings-row .desc,.tc-feature-copy,.tc-path-copy,.tc-loadout-meta,
  .tc-loadout-detail,.tc-target-enter,.tc-report-note,.tc-comp-pair{
    font-size:13px!important;line-height:1.45!important
  }
  .tc-kicker,.tc-report-kicker,.tc-comp-number,.tc-bearing-kind,.tc-report-stamp,
  .tc-forge-favor .tc-kicker,.tc-contract-facts span,.tc-workbench-credit,
  .tc-comp-mod>span,.tc-comp-weapons span{
    font-size:9.5px!important;line-height:1.25!important;letter-spacing:.09em!important
  }

  /* Top bars / navigation */
  .tc-brand-small{font-size:15px!important}
  .tc-sync{font-size:9px!important}
  .tc-bottom-nav button{font-size:9.5px!important;line-height:1.15!important;min-height:52px!important;padding:7px 3px!important}
  .tc-ledger-tabs button{font-size:9.5px!important;line-height:1.2!important;min-height:48px!important;letter-spacing:.045em!important}

  /* Hub */
  .tc-title{font-size:clamp(38px,11vw,50px)!important;line-height:.98!important}
  .tc-subtitle{font-size:12px!important}
  .tc-value{font-size:21px!important;line-height:1.15!important}
  .tc-panel{padding:15px 13px!important}

  /* Encounter briefing */
  .tc-brief-boss{font-size:clamp(31px,9.5vw,43px)!important;line-height:1.02!important}
  .tc-brief-flavor{font-size:14px!important;line-height:1.45!important}
  .tc-loadout-name{font-size:23px!important;line-height:1.08!important}
  .tc-loadout-role{font-size:11px!important;line-height:1.3!important}
  .tc-loadout-row dt{font-size:9px!important}
  .tc-loadout-row dd{font-size:13px!important;line-height:1.35!important}
  .tc-rite-name,.tc-weird-name{font-size:23px!important;line-height:1.1!important}
  .tc-rite-text,.tc-rtext,.tc-chaos-trigger,.tc-trigger-copy{font-size:15px!important;line-height:1.45!important}
  .tc-chaos-event-name,.tc-chaos-consequence{line-height:1.18!important}
  .tc-chaos-consequence{font-size:15px!important}
  .tc-chaos-quip{font-size:12.5px!important;line-height:1.35!important}
  .btn{font-size:10.5px!important;line-height:1.2!important;min-height:52px!important}

  /* Post-battle */
  .tc-report-victory{font-size:38px!important}
  .tc-report-boss{font-size:27px!important;line-height:1.08!important}
  .tc-report-row{grid-template-columns:1fr!important;gap:8px!important;padding:13px 4px!important}
  .tc-report-choices{width:100%!important;min-width:0!important}
  .tc-report-choices button{font-size:10px!important;min-height:46px!important}
  .tc-report-total{font-size:9px!important}
  .tc-report-total strong{font-size:30px!important}

  /* Ledger / compendium */
  .tc-ledger-count{font-size:30px!important}
  .tc-rem,.tc-region-chip,.tc-bearing{font-size:13px!important;line-height:1.35!important}
  .tc-rem .stamp,.tc-bearing-stamp{font-size:8.5px!important}
  .tc-comp-title{font-size:28px!important;line-height:1.05!important}
  .tc-comp-stats strong{font-size:23px!important}
  .tc-comp-stats span{font-size:8px!important}
  .tc-comp-boss{font-size:24px!important;line-height:1.08!important}
  .tc-comp-mark{font-size:8px!important}
  .tc-comp-weapons{grid-template-columns:1fr!important}
  .tc-comp-weapons>div+div{border-left:0!important;border-top:1px solid var(--line-soft)!important}
  .tc-comp-weapons strong{font-size:18px!important;line-height:1.15!important}
  .tc-comp-weapons em{font-size:11px!important;white-space:normal!important}
  .tc-comp-mod strong{font-size:17px!important;line-height:1.2!important}
  .tc-comp-footer{font-size:8.5px!important;line-height:1.3!important}

  /* Smithing / rewards */
  .tc-forge-favor strong{font-size:31px!important}
  .tc-forge-title{font-size:18px!important;line-height:1.15!important}
  .tc-boon-grid strong{font-size:28px!important}
  .tc-boon-grid span{font-size:8px!important;line-height:1.25!important}
  .tc-boon-grid{grid-template-columns:1fr!important}
  .tc-bearing strong{font-size:15px!important;line-height:1.25!important}
  .tc-bearing small{font-size:11px!important;line-height:1.3!important}
  .tc-contract-sheet h2{font-size:28px!important;line-height:1.05!important}
  .tc-contract-facts strong{font-size:14px!important;line-height:1.3!important}
  .tc-contract-demand p,.tc-contract-sanction p{font-size:14px!important;line-height:1.45!important}

  /* Settings */
  .tc-settings-row{min-height:68px!important;padding-top:12px!important;padding-bottom:12px!important}
  .tc-settings-row .name{font-size:16px!important;line-height:1.15!important}

  /* Give dense two-column cards permission to stack instead of shrinking. */
  .tc-hub-grid{grid-template-columns:1fr!important}
  .tc-hub-grid>.tc-panel{grid-column:1!important}
}

/* Very narrow phones: preserve readability rather than squeezing. */
@media (max-width: 370px) {
  .app-shell{padding-left:10px;padding-right:10px}
  .tc-bottom-nav button{font-size:9px!important}
  .tc-ledger-tabs button{font-size:9px!important;padding-left:2px!important;padding-right:2px!important}
  .tc-brief-boss{font-size:30px!important}
  .tc-loadout-name{font-size:21px!important}
  .tc-muted,.tc-report-detail,.tc-comp-mod p,.tc-settings-row .desc{font-size:12.5px!important}
}
'''

if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in ['Phone readability pass', '.tc-bottom-nav button{font-size:9.5px', '.tc-loadout-name{font-size:23px', '.tc-settings-row .name{font-size:16px']:
    if needle not in s:
        raise SystemExit('mobile readability invariant missing: ' + needle)

p.write_text(s)
