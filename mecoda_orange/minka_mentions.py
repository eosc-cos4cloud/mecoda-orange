import Orange.data
import pandas as pd
from mecoda_minka import get_dfs, get_obs
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview
from orangewidget.widget import Input, Output, OWBaseWidget


def get_user_df(df: pd.DataFrame) -> pd.DataFrame:
    users = []
    for user in df.user_login.unique():
        url = f"https://minka-sdg.org/users/{user}"
        user_dict = {
            "user": user,
            "user_url": url,
            "observations": len(df[df["user_login"] == user]),
        }
        users.append(user_dict)

    df_users = pd.DataFrame(users)
    df_users_sorted = df_users.sort_values(
        by=["observations"], ascending=False
    ).reset_index(drop=True)
    return df_users_sorted


class MinkaMentionsWidget(OWBaseWidget):
    name = "Minka Mentions"
    description = "Get users that contribute to a dataset of observations from Minka"
    icon = "icons/minka-users.png"
    priority = 6
    want_main_area = False
    resizing_enabled = False

    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        mentions = Output("mentions", Orange.data.Table, auto_summary=False)

    def __init__(self):
        super().__init__()

        infoBox = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(infoBox, "No observations fetched yet.")
        self.infob = gui.widgetLabel(infoBox, "")

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            df = table_to_frame(dataset)
            self.infoa.setText(f"{len(df.user_login.unique())} users in input dataset")
            df_users = get_user_df(df)
        out = table_from_frame(df_users)
        self.Outputs.mentions.send(out)


if __name__ == "__main__":
    WidgetPreview(MinkaMentionsWidget).run()
