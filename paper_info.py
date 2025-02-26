from argparse import ArgumentError


class PaperInfo:
    def __init__(self, index_str):
        self.index_str = index_str
        self.title = ""
        self.first_author_emails = ""
        self.last_author_emails = ""
        self.all_author_emails = ""
        self.author_href_list = []

# class

def parse_paper_list_file(paper_file, paper_type=None):
    """
    paper_type is like: oral, spotlight, poster
    the paper info file looks like ================================
    [paper]
    # paper        : 1
    # page         : 1
    # paper_in_page: 1
    How new data pollutes LLM knowledge and how to dilute it
        https://openreview.net/profile?id=~Chen_Sun7
        https://openreview.net/profile?id=~Renat_Aksitov1
        https://openreview.net/profile?id=~Andrey_Zhmoginov1
        https://openreview.net/profile?id=~Nolan_Andrew_Miller1
        https://openreview.net/profile?id=~Max_Vladymyrov1
        https://openreview.net/profile?id=~Ulrich_Rueckert1
        https://openreview.net/profile?id=~Been_Kim1
        https://openreview.net/profile?id=~Mark_Sandler1

    """
    if paper_type is None or paper_type == "":
        if 'oral' in paper_file:
            paper_type = 'oral'
        elif 'spotlight' in paper_file:
            paper_type = 'spotlight'
        else:
            raise ArgumentError(f"Can not parse paper_type from paper_file name")

    with open(paper_file, "r") as f:
        lines = f.readlines()
    pi_list = []    # PaperInfo list
    pi_idx = 0      # paper index
    pi = None       # PaperInfo
    for line in lines:
        if line.startswith("#"):
            continue
        elif line.startswith('[paper]'):   # new paper info unit
            pi_idx = pi_idx + 1
            pi = PaperInfo(f"{paper_type}{pi_idx:03d}")
        elif line.startswith("    "):
            pi.author_href_list.append(line.strip())
        elif line.strip() == '':        # means end of paper info unit
            if pi is not None:
                pi_list.append(pi)
                pi = None
        else:
            pi.title = line.strip()
    # for
    if pi is not None:
        pi_list.append(pi)
    return pi_list

def replenish_emails_to_pi_list(pi_list, author_file):
    """
    replenish Emails to each PaperInfo in the PaperInfo list.
    :param pi_list:
    :param author_file:
    :return:
    """
    with open(author_file, "r") as f:
        lines = f.readlines()
    href_map = {}
    for line in lines:
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        href, emails = line.split(": ")
        href = href.strip()
        emails = emails.strip()
        href_map[href] = emails
    # for
    print(f"author_file : {author_file}")
    print(f"author count: {len(href_map)}")
    for pi in pi_list:
        href_list = pi.author_href_list
        href = href_list[0]     # ------------------- first author emails
        if href in href_map:
            pi.first_author_emails = href_map[href]
        else:
            print(f"Error: not found email for: {href}")
        href = href_list[-1]    # ------------------- last author emails
        if href in href_map:
            pi.last_author_emails = href_map[href]
        else:
            print(f"Error: not found email for: {href}")
        tmp = ""                # ------------------- all author emails
        for href in href_list:
            if href in href_map:
                tmp += href_map[href]
            else:
                print(f"Error: not found email for: {href}")
        # for
        pi.all_author_emails = tmp
    # for

def save_pi_list_by_first_author(pi_list, res_file):
    """
    Save PaperInfo list by first author, specifying his/her Emails.
    :param pi_list:
    :param res_file:
    :return:
    """
    with open(res_file, "w") as f:
        for pi in pi_list:
            f.write(f"{pi.index_str}: {pi.author_href_list[0]} : {pi.first_author_emails}\n")
        # for
    # with

def save_pi_list_by_last_author(pi_list, res_file):
    """
    Save PaperInfo list by last author, specifying his/her Emails.
    :param pi_list:
    :param res_file:
    :return:
    """
    with open(res_file, "w") as f:
        for pi in pi_list:
            f.write(f"{pi.index_str}: {pi.author_href_list[-1]} : {pi.last_author_emails}\n")
        # for
    # with

def save_pi_list_by_all_author(pi_list, res_file):
    """
    Save PaperInfo list by all author, specifying their Emails.
    :param pi_list:
    :param res_file:
    :return:
    """
    with open(res_file, "w") as f:
        for pi in pi_list:
            f.write(f"{pi.index_str}: {pi.all_author_emails}\n")
        # for
    # with

def replenish_emails(paper_file_list, author_file):
    pi_list = []
    for paper_file in paper_file_list:
        _ = parse_paper_list_file(paper_file, paper_type=None)
        print(f"paper_file : {paper_file}")
        print(f"paper count: {len(_)}")
        pi_list.extend(_)
    print(f"pi_list all: {len(pi_list)}")
    replenish_emails_to_pi_list(pi_list, author_file)

    f_path1 = "./res_paper_with_first_author_emails.txt"
    save_pi_list_by_first_author(pi_list, f_path1)
    print(f"File saved: {f_path1}")

    f_path1 = "./res_paper_with_last_author_emails.txt"
    save_pi_list_by_last_author(pi_list, f_path1)
    print(f"File saved: {f_path1}")

    f_path2 = "./res_paper_with_all_author_emails.txt"
    save_pi_list_by_all_author(pi_list, f_path2)
    print(f"File saved: {f_path2}")

