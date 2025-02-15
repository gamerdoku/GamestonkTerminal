""" Seeking Alpha View """
__docformat__ = "numpy"

import os
from datetime import datetime
from tabulate import tabulate
import pandas as pd
from gamestonk_terminal.helper_funcs import export_data

from gamestonk_terminal.stocks.discovery import seeking_alpha_model


def upcoming_earning_release_dates(num_pages: int, num_earnings: int, export: str):
    """Displays upcoming earnings release dates

    Parameters
    ----------
    num_pages: int
        Number of pages to scrap
    num_earnings: int
        Number of upcoming earnings release dates
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    # TODO: Check why there are repeated companies
    # TODO: Create a similar command that returns not only upcoming, but antecipated earnings
    # i.e. companies where expectation on their returns are high

    df_earnings = seeking_alpha_model.get_next_earnings(num_pages)

    pd.set_option("display.max_colwidth", None)
    if export:
        l_earnings = []
        l_earnings_dates = []

    for n_days, earning_date in enumerate(df_earnings.index.unique()):
        if n_days > (num_earnings - 1):
            break

        # TODO: Potentially extract Market Cap for each Ticker, and sort
        # by Market Cap. Then cut the number of tickers shown to 10 with
        # bigger market cap. Didier attempted this with yfinance, but
        # the computational time involved wasn't worth pursuing that solution.

        df_earn = df_earnings[earning_date == df_earnings.index][
            ["Ticker", "Name"]
        ].dropna()

        if export:
            l_earnings_dates.append(earning_date.date())
            l_earnings.append(df_earn)

        df_earn.index = df_earn["Ticker"].values
        df_earn.drop(columns=["Ticker"], inplace=True)

        print(
            tabulate(
                df_earn,
                showindex=True,
                headers=[f"Earnings on {earning_date.date()}"],
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    if export:
        for i, _ in enumerate(l_earnings):
            l_earnings[i].reset_index(drop=True, inplace=True)
        df_data = pd.concat(l_earnings, axis=1, ignore_index=True)
        df_data.columns = l_earnings_dates

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "upcoming",
            df_data,
        )


def news(news_type: str, article_id: int, num: int, start_date: datetime, export: str):
    """Prints the latest news article list. [Source: Seeking Alpha]

    Parameters
    ----------
    news_type: str
        Select between 'latest' or 'trending'
    article_id: int
        Article ID. If -1, none is selected
    num: int
        Number of articles to display. Only used if article_id is -1.
    start_date : datetime
        Date from when to get articles dates. Only used if article_id is -1.
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    # User wants to see all latest news
    if article_id == -1:
        if news_type == "latest":
            articles = seeking_alpha_model.get_article_list(start_date, num)
        elif news_type == "trending":
            articles = seeking_alpha_model.get_trending_list(num)
        else:
            print("Wrong type of news selected", "\n")

        if export:
            df_articles = pd.DataFrame(articles)

        for idx, article in enumerate(articles):
            print(
                article["publishedAt"].replace("T", " ").replace("Z", ""),
                "-",
                article["id"],
                "-",
                article["title"],
            )
            print(article["url"])
            print("")

            if idx >= num - 1:
                break

    # User wants to access specific article
    else:
        if news_type == "latest":
            article = seeking_alpha_model.get_article_data(article_id)
        elif news_type == "trending":
            article = seeking_alpha_model.get_article_data(article_id)
        else:
            print("Wrong type of news selected", "\n")

        if export:
            df_articles = pd.DataFrame(article)

        print(
            article["publishedAt"][: article["publishedAt"].rfind(":") - 3].replace(
                "T", " "
            ),
            " ",
            article["title"],
        )
        print(article["url"])
        print("")
        print(article["content"])

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            news_type,
            df_articles,
        )
