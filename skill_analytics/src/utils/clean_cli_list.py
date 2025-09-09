def clean_cli_list(cli_list):
    return [x.replace(",", "").strip() for x in cli_list]