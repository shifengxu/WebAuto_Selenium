"""
pip install selenium
"""
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

class AuthorExtractor:
    def __init__(self):
        self.author_href_set = set()

    @staticmethod
    def find_or_sleep(ele, by, value):
        # find element, if not exist, sleep for a while and find again.
        sleep_count = 5
        lst = ele.find_elements(by, value)
        while sleep_count > 0 and len(lst) == 0:
            time.sleep(1)
            sleep_count -= 1
        return ele.find_element(by, value)

    def login(self, driver):
        li_user = self.find_or_sleep(driver, By.ID, "user-menu")
        li_user.click()
        time.sleep(2)
        input_email = self.find_or_sleep(driver, By.ID, "email-input")
        input_email.send_keys("shifeng001@e.ntu.edu.sg")
        time.sleep(2)
        input_password = self.find_or_sleep(driver, By.ID, "password-input")
        input_password.send_keys("xxx")
        time.sleep(2)
        btn_login = self.find_or_sleep(driver, By.CSS_SELECTOR, "button.btn.btn-login")
        btn_login.click()
        time.sleep(2)

    def parse_papers(self, page_url, res_file_paper):
        driver = webdriver.Chrome()
        driver.get(page_url)
        time.sleep(5)
        print("Page url  :", page_url)
        print("Page Title:", driver.title)

        def parse_title_and_authors(_unit_div):
            h4 = _unit_div.find_element(By.CSS_SELECTOR, "h4")
            a_title = h4.find_element(By.CSS_SELECTOR, "a").text
            a_title = re.sub(r"\s+", " ", a_title)
            fptr.write(f"[paper]\n")
            fptr.write(f"# paper        : {paper_idx}\n")
            fptr.write(f"# page         : {page_idx}\n")
            fptr.write(f"# paper_in_page: {paper_idx_in_page}\n")
            fptr.write(f"{a_title}\n")
            span_authors = unit_div.find_element(By.CSS_SELECTOR, "div.note-authors span")
            a_author_list = span_authors.find_elements(By.CSS_SELECTOR, "a")
            href_list = []
            for a_author in a_author_list:
                href = a_author.get_attribute("href")
                if "profile?" not in href:
                    continue  # some <a> href:  https://openreview.net/group?id=ICLR.cc/2025/Conference#
                fptr.write(f"    {href}\n")
                href_list.append(href)
                if href not in self.author_href_set:
                    self.author_href_set.add(href)
            # for
            return a_title, href_list

        paper_idx = 0       # paper index, this is global index
        page_idx = 0        # page index
        # page_url has such format:
        # https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-accept-oral
        # https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-accept-spotlight
        # Here, we have to use the element ID to find the correct <div> element.
        # Because there are many similar html-subtree for different type (oral, spotlight, poster),
        # and the only difference of those subtrees are the header <div> ID.
        div_id = page_url.split("tab-")[-1]
        fptr = open(res_file_paper, "w", errors="ignore")
        while True:
            div_by_id = driver.find_element(By.ID, div_id)
            div_element = div_by_id.find_element(By.CSS_SELECTOR, "div.submissions-list")
            ul_element = div_element.find_element(By.CSS_SELECTOR, "ul.list-unstyled.list-paginated")
            unit_div_elements = ul_element.find_elements(By.CSS_SELECTOR, "div.note.undefined")

            page_idx += 1
            paper_idx_in_page = 0
            for unit_div in unit_div_elements:  # loop every paper unit: title and authors
                paper_idx += 1
                paper_idx_in_page += 1
                title, a_list = parse_title_and_authors(unit_div)
                print(f"{paper_idx_in_page:02d} of page{page_idx:02d}: [{paper_idx:3d}] {title} <- {len(a_list)}")
                fptr.write(f"\n")
                fptr.flush()
            # for
            # pagination
            ul_pagination = div_element.find_element(By.CSS_SELECTOR, "ul.pagination")
            li_right_arrow = ul_pagination.find_element(By.CSS_SELECTOR, "li.right-arrow")
            li_right_arrow_class_str = li_right_arrow.get_attribute("class")
            print(f"    li_right_arrow_class_str: {li_right_arrow_class_str}")
            if 'disabled' in li_right_arrow_class_str:
                print(f"    next-page button is disabled. will end the loop.")
                break   # break the while loop
            else:
                li_right_arrow.find_element(By.CSS_SELECTOR, "span").click()
                print(f"    clicked for next page...")
                print(f"    sleep 5 seconds")
                time.sleep(5)
                print(f"")
        # while
        fptr.close()
        print(f"File saved: {res_file_paper}")
        driver.quit()
        time.sleep(2)

    def parser_authors(self, res_author_href, res_file_author_email):
        with open(res_author_href, "r") as f:
            line_arr = f.readlines()
        href_arr = []
        for line in line_arr:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            href_arr.append(line)
        print(f"res_author_href : {res_author_href}")
        print(f"href total count: {len(href_arr)}")

        f_dir, f_name = os.path.split(res_file_author_email)
        stem, ext = os.path.splitext(f_name)
        res_author_exception = os.path.join(f_dir, f"{stem}_exception{ext}")
        f_email_ptr = open(res_file_author_email, "w")
        f_exc_ptr   = open(res_author_exception, "w")
        driver = webdriver.Chrome()
        for _idx, href in enumerate(self.author_href_set):
            idx = _idx + 1
            try:
                driver.get(href)
                time.sleep(2)
                if idx == 1:
                    self.login(driver)
                section_emails = self.find_or_sleep(driver, By.CSS_SELECTOR, "section.emails")
                div_compact    = self.find_or_sleep(section_emails, By.CSS_SELECTOR, "div.list-compact")
                div_list = div_compact.find_elements(By.CSS_SELECTOR, "div")
                email_list = []
                for div in div_list:
                    span = div.find_element(By.CSS_SELECTOR, "span")
                    email = span.text.strip()
                    email_list.append(email)
                # for
                email_str_list = [f"{email};" for email in email_list]
                email_str_all = "".join(email_str_list)
                f_email_ptr.write(f"{href}: {email_str_all}\n")
                f_email_ptr.flush()
                print(f"{idx:4d} {href}: {email_str_all}")
            except Exception as e:
                f_exc_ptr.write(f"{idx:4d}: {href}\n")
                f_exc_ptr.write(str(e))
                f_exc_ptr.write("\n\n\n")
                f_exc_ptr.flush()
        # for
        f_email_ptr.close()
        f_exc_ptr.close()
        print(f"File saved: {res_file_author_email}")
        print(f"File saved: {res_author_exception}")

        driver.quit()
        time.sleep(2)

def main():
    ae = AuthorExtractor()
    page_url_oral = f"https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-accept-oral"
    page_url_spot = f"https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-accept-spotlight"
    res_author_href  = f"./res_author_href.txt"
    res_author_email = f"./res_author_email.txt"
    ae.parse_papers(page_url_oral, f"./res_paper_oral.txt")
    ae.parse_papers(page_url_spot, f"./res_paper_spotlight.txt")
    with open(res_author_href, "w") as f: [f.write(f"{href}\n") for href in ae.author_href_set]
    print(f"File saved: {res_author_href}")

    ae.parser_authors(res_author_href, res_author_email)

    from paper_info import replenish_emails
    paper_file_list = [f"./res_paper_oral.txt", f"./res_paper_spotlight.txt"]
    replenish_emails(paper_file_list, res_author_email)

if __name__ == '__main__':
    main()
