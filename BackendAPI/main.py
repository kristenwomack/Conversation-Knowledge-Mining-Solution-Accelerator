import uvicorn
from typing import Union, List
from fastapi import FastAPI, HTTPException, status
from config import config
import logging
from databases.sql_service import get_db_connection, adjust_dates, get_filters_metrics, get_charts_metrics
from models.input_models import ChartFilters, SelectedFilters


app = FastAPI()


@app.get("/get_metrics")
def get_metrics(data_type: str = 'filters') -> Union[List[dict], dict]:
    """
    Get metrics from the database
    :param data_type: str. Default is 'filters'. Can be 'filters' or 'charts'.
    """
    try:
        # Validate the data type
        data_type = data_type.lower()
        if data_type not in ['filters', 'charts']:
            logging.error("Invalid data type. Please provide a valid data type.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data type. Please provide a valid data type.")
    
        conn = get_db_connection()

        # Adjust the dates in the processed_data table to the current date
        adjust_dates(conn)

        # Get the metrics
        if data_type == 'filters':
            # Get metrics for the filters
            filters_metrics = get_filters_metrics(conn)
            conn.close()
            return filters_metrics

        elif data_type == 'charts':
            # Get metrics for the charts
            charts_metrics = get_charts_metrics(conn)
            conn.close()
            return charts_metrics
    
    except Exception as e:
        logging.error(f"An error occurred while getting metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting {data_type} metrics")


@app.post("/get_metrics")
def chart_metrics(chart_filters: ChartFilters) -> Union[List[dict], dict]:
    """
    Get metrics for the charts
    :param chart_filters: ChartFilters. The filters for the charts.
    """
    try:
        conn = get_db_connection()

        # Adjust the dates in the processed_data table to the current date
        adjust_dates(conn)

        # Get the metrics for the charts
        charts_metrics = get_charts_metrics(conn, chart_filters)
        conn.close()

        return charts_metrics
    except Exception as e:
        logging.error(f"An error occurred while getting chart metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting chart metrics")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)