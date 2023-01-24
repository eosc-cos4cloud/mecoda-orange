from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import pandas as pd
from datetime import timedelta

def _prepare_df(df):
    # eliminamos los olores de categoría "No Odour"
    clean_df = df[df['category'] != "No Odour"].reset_index(drop=True)

    # construimos la columna con fecha y hora
    clean_df['date_time'] = pd.to_datetime(
        clean_df['date'].astype(str) + " " + clean_df['time_hour'].astype(str) +":"+ clean_df['time_min'].astype(str) +":"+ df['time_sec'].astype(str)) 

    # eliminamos registros duplicados
    clean_df = clean_df[-clean_df.duplicated()]

    clean_df = clean_df.sort_values(by="date_time").reset_index(drop=True)

    # creamos columna con ids únicos de los registros (no existente en el df)
    clean_df = clean_df.reset_index()
    clean_df.rename(columns={'index': 'idx'}, inplace=True)

    # creamos un index de fecha
    clean_df.index = pd.DatetimeIndex(clean_df['date_time'])
    clean_df = clean_df.sort_index()
    return clean_df 

# cálculo de los eventos por categoría/tipo
def _get_mm(row):
    matriz_molestia = {
        4: [1,1,2,2,2,3],
        3: [1,2,2,3,3,4],
        2: [2,2,3,3,4,4],
        1: [3,3,4,4,4,5],
        0: [3,4,4,5,5,5],
        -1: [4,4,5,5,6,6],
        -2: [5,5,5,6,6,7],
        -3:	[5,6,6,7,7,7],
        -4:	[6,6,7,7,7,7],
        }
    total = 0
    for i in range(len(row.hedonic_tone)):
        molestia = matriz_molestia[int(row['hedonic_tone'][i])][int(row['intensity'][i]) - 1]
        total += molestia
    return total


def _get_event_list(df, col):
    total_events = []

    for category in df[col].unique():
        # creamos una lista de eventos agrupada por categoría/tipo 
        # según hayamos pasado ese parámetro en la función
        cat_events = []
        event = None

        for idx, obs in df[df[col] == category].iterrows():
            if event is not None:
                if obs['date_time'] <= (event['last_end_hour'] + timedelta(hours=4)):
                    if obs['user'] not in event['users']:
                        event['last_end_hour'] = obs.date_time
                        event['event_code'] = f"event"
                        event[col] = category
                        event['obs_ids'].append(obs.idx)
                        event['hedonic_tone'].append(obs.hedonic_tone_n)
                        event['intensity'].append(obs.intensity_n)
                        event['users'].append(obs.user)
                else:
                    if len(event['obs_ids']) > 1:
                        cat_events.append(event)

                    event = {}
                    event['start'] = obs.date_time
                    event['event_code'] = "posible"
                    event['obs_ids'] = [obs.idx]
                    event[col] = category
                    event['last_end_hour'] = obs.date_time
                    event['hedonic_tone'] = [obs.hedonic_tone_n]
                    event['intensity'] = [obs.intensity_n]
                    event['users'] = [obs.user]
            else:
                event = {
                    'start': obs.date_time,
                    "event_code": "posible",
                    "obs_ids": [obs.idx],
                    "last_end_hour": obs.date_time,
                    "hedonic_tone": [obs.hedonic_tone_n],
                    "intensity": [obs.intensity_n],
                    "users": [obs.user]
                }
        total_events.extend(cat_events)
    return total_events

def get_events(df, col):
    #df = _prepare_df(df)
    total_events = _get_event_list(df, col)

    # construir df con todos los eventos
    df_eventos = pd.DataFrame(total_events)

    # creamos código único para cada evento
    df_eventos = df_eventos.reset_index(drop=False)
    df_eventos['event_code'] = df_eventos['event_code'] + "_" + df_eventos["index"].astype(str)
    df_eventos = df_eventos.drop(columns="index")

    # creamos columna de número de registros del evento
    df_eventos['num_obs'] = df_eventos['obs_ids'].apply(lambda x: len(x))

    # ordenamos las columnas
    df_eventos = df_eventos[["event_code", 'start', 'last_end_hour', col, "obs_ids", "hedonic_tone", "intensity", "users", "num_obs"]]

    # cálculo del grado de molestia
    df_eventos['MM'] = df_eventos.apply(_get_mm, axis=1)
    
    df_eventos['num_users'] = df_eventos["users"].apply(lambda x: len(x))

    # verificar esta formula
    df_eventos['GM'] = round(df_eventos["MM"] / (df_eventos.num_users * 7)*100, 2)

    # convertir listas en strings
    df_eventos['obs_ids'] = df_eventos['obs_ids'].astype(str)
    df_eventos['hedonic_tone'] = df_eventos['hedonic_tone'].astype(str)
    df_eventos['intensity'] = df_eventos['intensity'].astype(str)
    df_eventos['users'] = df_eventos['users'].astype(str)
    
    return df_eventos

class EventsWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Odour Collect Events"
    # Short widget description
    description = "Splits Table of odour observations into two dataframes: one for events grouped by category and other for events grouped by type."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/odourcollect-logo2.png"
    priority = 7

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Inputs and outputs
    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        type_events = Output("type_events", Orange.data.Table, auto_summary=False)
        category_events = Output(
            "category_events", Orange.data.Table, auto_summary=False)
        all_data = Output(
            "all_data", Orange.data.Table, auto_summary=False)


    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, 'No data on input yet, waiting to get something.')


    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText(f'{len(dataset)} instances in input dataset')
            df = table_to_frame(dataset)
            clean_df = _prepare_df(df)

            df_type = get_events(clean_df, "type")
            df_category = get_events(clean_df, "category")
            
            type_events = table_from_frame(df_type)
            category_events = table_from_frame(df_category)
            
            # modify clean_df to allow conversion to table
            clean_df = clean_df.drop(columns="date_time")
            clean_df["idx"] = clean_df["idx"].astype("str")
            clean_df.idx = pd.Categorical(clean_df.idx)

            all_data = table_from_frame(clean_df)

            self.infoa.setText(f'Events by type: {len(df_type)}')
            #self.infob.setText(f'Events by category: {len(df)}')

            self.Outputs.type_events.send(type_events)
            self.Outputs.category_events.send(category_events)
            self.Outputs.all_data.send(all_data)

        else:
            self.infoa.setText(
                'No data on input yet, waiting to get something.')



if __name__ == "__main__":
    WidgetPreview(EventsWidget).run()