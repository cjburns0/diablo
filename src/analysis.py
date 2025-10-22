"""
Analysis module for Mount Diablo Challenge race data.
Provides statistical analysis and visualization functions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from database import DiabloDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiabloAnalyzer:
    """Analyzer for Mount Diablo Challenge race data."""

    def __init__(self, db_path=None):
        self.db = DiabloDatabase(db_path)
        self.db.connect()

    def close(self):
        """Close database connection."""
        self.db.close()

    def get_race_results_df(self):
        """Get all race results as a pandas DataFrame."""
        query = '''
            SELECT * FROM race_results
            ORDER BY year, place
        '''
        df = pd.read_sql_query(query, self.db.conn)
        return df

    def get_weather_data_df(self):
        """Get all weather data as a pandas DataFrame."""
        query = '''
            SELECT * FROM weather_data
            ORDER BY year, timestamp
        '''
        df = pd.read_sql_query(query, self.db.conn)
        return df

    def calculate_yearly_statistics(self):
        """Calculate comprehensive statistics for each year.

        Returns:
            pandas DataFrame with statistics by year
        """
        df = self.get_race_results_df()

        # Filter out null chip times
        df = df[df['chip_time_seconds'].notna()]

        # Group by year and calculate statistics
        stats = df.groupby('year')['chip_time_seconds'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('p25', lambda x: x.quantile(0.25)),
            ('p75', lambda x: x.quantile(0.75))
        ]).reset_index()

        # Convert seconds to HH:MM:SS format for readability
        time_columns = ['mean', 'median', 'min', 'max', 'p25', 'p75']
        for col in time_columns:
            stats[f'{col}_formatted'] = stats[col].apply(self.seconds_to_time_str)

        return stats

    def calculate_weather_statistics_by_year(self):
        """Calculate weather statistics for each year.

        Returns:
            pandas DataFrame with weather statistics by year and location
        """
        df = self.get_weather_data_df()

        if df.empty:
            logger.warning("No weather data available")
            return pd.DataFrame()

        # Group by year and location
        stats = df.groupby(['year', 'location']).agg({
            'temperature_2m': ['mean', 'min', 'max'],
            'windspeed_10m': ['mean', 'min', 'max'],
            'wind_gusts_10m': ['mean', 'max'],
            'winddirection_10m': 'mean'
        }).reset_index()

        # Flatten column names
        stats.columns = ['_'.join(col).strip('_') for col in stats.columns.values]

        return stats

    def get_combined_statistics(self):
        """Get combined race and weather statistics.

        Returns:
            pandas DataFrame with merged statistics
        """
        race_stats = self.calculate_yearly_statistics()
        weather_stats = self.calculate_weather_statistics_by_year()

        if weather_stats.empty:
            return race_stats

        # Pivot weather stats to have start and summit as separate columns
        weather_pivot = weather_stats.pivot_table(
            index='year',
            columns='location',
            values=['windspeed_10m_mean', 'windspeed_10m_max', 'wind_gusts_10m_max', 'temperature_2m_mean']
        )

        # Flatten column names
        weather_pivot.columns = ['_'.join(col).strip('_') for col in weather_pivot.columns.values]
        weather_pivot = weather_pivot.reset_index()

        # Merge race and weather stats
        combined = race_stats.merge(weather_pivot, on='year', how='left')

        return combined

    @staticmethod
    def seconds_to_time_str(seconds):
        """Convert seconds to HH:MM:SS format."""
        if pd.isna(seconds):
            return None

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"

    @staticmethod
    def time_str_to_minutes(seconds):
        """Convert seconds to minutes for cleaner visualization."""
        if pd.isna(seconds):
            return None
        return seconds / 60

    def plot_yearly_times_distribution(self, save_path=None):
        """Plot chip time distribution by year.

        Args:
            save_path: Path to save the figure (optional)
        """
        stats = self.calculate_yearly_statistics()

        if stats.empty:
            logger.warning("No data to plot")
            return

        # Convert to minutes for better readability
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)

        years = stats['year']
        mean_times = stats['mean'] / 60
        median_times = stats['median'] / 60
        p25_times = stats['p25'] / 60
        p75_times = stats['p75'] / 60

        # Plot lines
        ax.plot(years, mean_times, marker='o', label='Mean', linewidth=2, markersize=8)
        ax.plot(years, median_times, marker='s', label='Median', linewidth=2, markersize=8)
        ax.plot(years, p25_times, marker='^', label='25th Percentile', linewidth=2, markersize=8, linestyle='--')
        ax.plot(years, p75_times, marker='v', label='75th Percentile', linewidth=2, markersize=8, linestyle='--')

        # Fill between percentiles
        ax.fill_between(years, p25_times, p75_times, alpha=0.2, label='IQR (25th-75th)')

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Chip Time (minutes)', fontsize=12, fontweight='bold')
        ax.set_title('Mount Diablo Challenge: Chip Time Trends by Year', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")

        return fig

    def plot_times_with_wind(self, save_path=None):
        """Plot chip times with wind speed overlay.

        Args:
            save_path: Path to save the figure (optional)
        """
        combined = self.get_combined_statistics()

        if combined.empty:
            logger.warning("No data to plot")
            return

        fig, ax1 = plt.subplots(figsize=config.FIGURE_SIZE)

        years = combined['year']
        median_times = combined['median'] / 60

        # Plot chip times on primary y-axis
        color1 = 'tab:blue'
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Median Chip Time (minutes)', fontsize=12, fontweight='bold', color=color1)
        ax1.plot(years, median_times, marker='o', color=color1, linewidth=2, markersize=8, label='Median Time')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)

        # Create secondary y-axis for wind speed
        ax2 = ax1.twinx()

        # Plot wind speeds on secondary y-axis
        color2 = 'tab:red'
        ax2.set_ylabel('Wind Speed (mph)', fontsize=12, fontweight='bold', color=color2)

        # Check which wind columns are available
        if 'windspeed_10m_mean_summit' in combined.columns:
            wind_col = 'windspeed_10m_mean_summit'
            wind_gust_col = 'wind_gusts_10m_max_summit'
            location = 'Summit'
        elif 'windspeed_10m_mean_start' in combined.columns:
            wind_col = 'windspeed_10m_mean_start'
            wind_gust_col = 'wind_gusts_10m_max_start'
            location = 'Start'
        else:
            logger.warning("No wind data available")
            return fig

        wind_speeds = combined[wind_col]
        wind_gusts = combined[wind_gust_col]

        ax2.plot(years, wind_speeds, marker='s', color=color2, linewidth=2, markersize=8,
                label=f'Avg Wind Speed ({location})', linestyle='--')
        ax2.plot(years, wind_gusts, marker='^', color='darkred', linewidth=2, markersize=8,
                label=f'Max Wind Gust ({location})', linestyle=':')
        ax2.tick_params(axis='y', labelcolor=color2)

        # Add title
        plt.title('Mount Diablo Challenge: Performance vs Wind Conditions', fontsize=14, fontweight='bold')

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")

        return fig

    def plot_wind_comparison(self, save_path=None):
        """Plot wind speed comparison between start and summit locations.

        Args:
            save_path: Path to save the figure (optional)
        """
        weather_stats = self.calculate_weather_statistics_by_year()

        if weather_stats.empty:
            logger.warning("No weather data to plot")
            return

        # Pivot to get start and summit side by side
        pivot_avg = weather_stats.pivot_table(
            index='year',
            columns='location',
            values='windspeed_10m_mean'
        ).reset_index()

        pivot_max = weather_stats.pivot_table(
            index='year',
            columns='location',
            values='wind_gusts_10m_max'
        ).reset_index()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Plot average wind speeds
        if 'start' in pivot_avg.columns and 'summit' in pivot_avg.columns:
            ax1.plot(pivot_avg['year'], pivot_avg['start'], marker='o', label='Start', linewidth=2, markersize=8)
            ax1.plot(pivot_avg['year'], pivot_avg['summit'], marker='s', label='Summit', linewidth=2, markersize=8)
            ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Average Wind Speed (mph)', fontsize=12, fontweight='bold')
            ax1.set_title('Average Wind Speed: Start vs Summit', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3)

        # Plot max wind gusts
        if 'start' in pivot_max.columns and 'summit' in pivot_max.columns:
            ax2.plot(pivot_max['year'], pivot_max['start'], marker='o', label='Start', linewidth=2, markersize=8)
            ax2.plot(pivot_max['year'], pivot_max['summit'], marker='s', label='Summit', linewidth=2, markersize=8)
            ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Max Wind Gust (mph)', fontsize=12, fontweight='bold')
            ax2.set_title('Max Wind Gusts: Start vs Summit', fontsize=14, fontweight='bold')
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")

        return fig

    def generate_all_plots(self, output_dir=None):
        """Generate all analysis plots.

        Args:
            output_dir: Directory to save plots (default: config.CHARTS_DIR)
        """
        if output_dir is None:
            output_dir = config.CHARTS_DIR

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        logger.info("Generating all analysis plots...")

        # Plot 1: Yearly time distribution
        self.plot_yearly_times_distribution(
            save_path=os.path.join(output_dir, 'yearly_times_distribution.png')
        )

        # Plot 2: Times with wind overlay
        self.plot_times_with_wind(
            save_path=os.path.join(output_dir, 'times_vs_wind.png')
        )

        # Plot 3: Wind comparison
        self.plot_wind_comparison(
            save_path=os.path.join(output_dir, 'wind_comparison.png')
        )

        logger.info(f"All plots saved to {output_dir}")

    def print_summary_statistics(self):
        """Print summary statistics to console."""
        logger.info("\n" + "="*80)
        logger.info("RACE STATISTICS SUMMARY")
        logger.info("="*80)

        stats = self.calculate_yearly_statistics()
        print(stats.to_string(index=False))

        logger.info("\n" + "="*80)
        logger.info("WEATHER STATISTICS SUMMARY")
        logger.info("="*80)

        weather_stats = self.calculate_weather_statistics_by_year()
        if not weather_stats.empty:
            print(weather_stats.to_string(index=False))
        else:
            logger.info("No weather data available")


def main():
    """Test analysis functions."""
    analyzer = DiabloAnalyzer()

    # Print summary statistics
    analyzer.print_summary_statistics()

    # Generate plots
    # analyzer.generate_all_plots()

    analyzer.close()


if __name__ == '__main__':
    main()
