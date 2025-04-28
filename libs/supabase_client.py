from datetime import datetime, date

from supabase import create_client
from postgrest.types import CountMethod

from libs.utils import retry_on_db_error
from libs.data import Districts


class Supabase:
    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)

    @retry_on_db_error()
    def get_concerts(self) -> list[dict]:
        """Fetch all concerts from the database."""
        response = self.client.table("concert").select("*").order("date", desc=True).execute()
        return response.data if response.data else []


    @retry_on_db_error()
    def get_stats(self) -> tuple[dict, dict, dict]:
        """Fetch yearly and monthly stats from the database."""
        # Get current year and month
        year_min = f"{date.today().year - 1}-01-01"
        year_max = f"{date.today().year}-01-01"

        response = (self.client.table("concert")
                               .select("id, date", count=CountMethod.exact)
                               .eq("is_cancelled", False)
                               .gte("date", year_min)
                               .lt("date", year_max)
                               .execute())
        
        year_stats = {}
        year_stats["previous"] = response.count if response.count else 0

        year_min = f"{date.today().year}-01-01"
        year_max = f"{date.today().year + 1}-01-01"

        response = (self.client.table("concert")
                               .select("id, date, district", count=CountMethod.exact)
                               .eq("is_cancelled", False)
                               .gte("date", year_min)
                               .lt("date", year_max)
                               .execute())
        
        year_stats["current"] =  response.count if response.count else 0
        
        district_stats = {}
        month_stats = {}
        for concert in response.data:
            # Count concerts by district
            district = concert["district"] if concert["district"] is not None else "Other"
            if district not in district_stats:
                district_stats[district] = 0
            district_stats[district] += 1
            
            # Count concerts by month
            date_obj = datetime.strptime(concert["date"], "%Y-%m-%d")
            month = int(date_obj.strftime("%m"))
            if month not in month_stats:
                month_stats[month] = 0
            month_stats[month] += 1
        
        # Fill missing districts with 0
        for district in Districts:
            if district not in district_stats:
                district_stats[district] = 0
        
        district_stats = dict(sorted(district_stats.items(), key=lambda x: x[1], reverse=True))
        
        # Fill missing months (1 to 12) with 0
        for month in range(1, 13):
            if month not in month_stats:
                month_stats[month] = 0
        
        return year_stats, district_stats, month_stats
    

    @retry_on_db_error()
    def save_concert(self, concert: dict) -> None:
        """Insert or update a concert in the database."""
        self.client.table("concert").upsert(concert, on_conflict="id").execute()


    @retry_on_db_error()
    def cancel_concert(self, concert_id: int) -> None:
        """Cancel a concert by its ID."""
        self.client.table("concert").update({"is_cancelled": True}).eq("id", concert_id).execute()
    

    @retry_on_db_error()
    def restore_concert(self, concert_id: int) -> None:
        """Restore a cancelled concert by its ID."""
        self.client.table("concert").update({"is_cancelled": False}).eq("id", concert_id).execute()
    

    @retry_on_db_error()
    def delete_concert(self, concert_id: int) -> None:
        """Delete a concert by its ID."""
        self.client.table("concert").delete().eq("id", concert_id).execute()