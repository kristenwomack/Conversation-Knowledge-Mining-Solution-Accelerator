from pydantic import BaseModel
from typing import List

class SelectedFilters(BaseModel):
    Topic: List
    Sentiment: List
    DateRange: List

class ChartFilters(BaseModel):
    selected_filters: SelectedFilters