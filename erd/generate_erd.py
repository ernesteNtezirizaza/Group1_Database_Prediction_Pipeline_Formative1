"""
Generate ERD Diagram using matplotlib
Creates a visual entity-relationship diagram
"""

import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch, ConnectionPatch
    
    def create_erd():
        """Create ERD diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(18, 14))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 16)
        ax.axis('off')
        
        # Title
        ax.text(10, 14, 'Hotel Booking Database - ERD', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        # Table 1: hotels (Top Left)
        x, y, width, height = 1, 10, 3.5, 2.5
        table_box = FancyBboxPatch((x, y), width, height,
                                   boxstyle="round,pad=0.1", 
                                   edgecolor='black', facecolor='lightblue', linewidth=2)
        ax.add_patch(table_box)
        
        ax.text(x + width/2, y + height - 0.3, 'hotels', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.plot([x, x + width], [y + height - 0.6, y + height - 0.6], 
                'k-', linewidth=2)
        
        fields = ['PK hotel_id', '    hotel_name', '    created_at']
        for i, field in enumerate(fields):
            ax.text(x + 0.2, y + height - 1.0 - i*0.4, field, 
                   ha='left', va='center', fontsize=9, family='monospace')
        
        # Table 2: guests (Bottom Left)
        x2, y2 = 1, 6
        table_box2 = FancyBboxPatch((x2, y2), width, height,
                                    boxstyle="round,pad=0.1", 
                                    edgecolor='black', facecolor='lightblue', linewidth=2)
        ax.add_patch(table_box2)
        
        ax.text(x2 + width/2, y2 + height - 0.3, 'guests', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.plot([x2, x2 + width], [y2 + height - 0.6, y2 + height - 0.6], 
                'k-', linewidth=2)
        
        fields2 = ['PK guest_id', '    country', '    is_repeated_guest', 
                  '    customer_type', '    created_at']
        for i, field in enumerate(fields2):
            ax.text(x2 + 0.2, y2 + height - 1.0 - i*0.4, field, 
                   ha='left', va='center', fontsize=9, family='monospace')
        
        # Table 3: bookings (Center)
        x3, y3 = 7, 4
        width3, height3 = 6, 6
        table_box3 = FancyBboxPatch((x3, y3), width3, height3,
                                    boxstyle="round,pad=0.1", 
                                    edgecolor='black', facecolor='lightcoral', linewidth=2)
        ax.add_patch(table_box3)
        
        ax.text(x3 + width3/2, y3 + height3 - 0.3, 'bookings', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.plot([x3, x3 + width3], [y3 + height3 - 0.6, y3 + height3 - 0.6], 
                'k-', linewidth=2)
        
        fields3 = [
            'PK booking_id', 'FK hotel_id', 'FK guest_id',
            'lead_time', 'arrival_date_year', 'arrival_date_month',
            'stays_in_weekend_nights', 'stays_in_week_nights',
            'adults', 'children', 'babies', 'meal',
            'market_segment', 'distribution_channel', 
            'previous_cancellations', 'adr',
            'reservation_status', 'is_canceled', 'created_at'
        ]
        for i, field in enumerate(fields3):
            ax.text(x3 + 0.2, y3 + height3 - 1.0 - i*0.35, field, 
                   ha='left', va='center', fontsize=8, family='monospace')
        
        # Table 4: booking_logs (Right)
        x4, y4 = 15, 4
        table_box4 = FancyBboxPatch((x4, y4), 3.5, 2.5,
                                    boxstyle="round,pad=0.1", 
                                    edgecolor='black', facecolor='lightgreen', linewidth=2)
        ax.add_patch(table_box4)
        
        ax.text(x4 + 1.75, y4 + height - 0.3, 'booking_logs', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.plot([x4, x4 + 3.5], [y4 + height - 0.6, y4 + height - 0.6], 
                'k-', linewidth=2)
        
        fields4 = ['PK log_id', 'FK booking_id', 'action', 
                  'old_status', 'new_status', 'timestamp']
        for i, field in enumerate(fields4):
            ax.text(x4 + 0.2, y4 + height - 1.0 - i*0.4, field, 
                   ha='left', va='center', fontsize=9, family='monospace')
        
        # Arrows: hotels → bookings
        ax.annotate('', xy=(x3, y3 + height3 - 0.5), xytext=(x + width, y + height/2),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        ax.text((x + width + x3)/2, (y + height/2 + y3 + height3 - 0.5)/2, 
               '1:N', ha='center', va='center', 
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))
        
        # Arrows: guests → bookings
        ax.annotate('', xy=(x3, y3 + height3/2), xytext=(x2 + width, y2 + height/2),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        ax.text((x2 + width + x3)/2, (y2 + height/2 + y3 + height3/2)/2, 
               '1:N', ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))
        
        # Arrows: bookings → booking_logs
        ax.annotate('', xy=(x4, y4 + height/2), xytext=(x3 + width3, y3 + height3 - 0.5),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        ax.text((x3 + width3 + x4)/2, (y3 + height3 + y4 + height/2)/2, 
               '1:N', ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))
        
        # Table 5: predictions (Below booking_logs)
        x5, y5 = 15, 1
        width5, height5 = 3.5, 3.5
        table_box5 = FancyBboxPatch((x5, y5), width5, height5,
                                    boxstyle="round,pad=0.1", 
                                    edgecolor='black', facecolor='plum', linewidth=2)
        ax.add_patch(table_box5)
        
        ax.text(x5 + width5/2, y5 + height5 - 0.3, 'predictions', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.plot([x5, x5 + width5], [y5 + height5 - 0.6, y5 + height5 - 0.6], 
                'k-', linewidth=2)
        
        fields5 = [
            'PK prediction_id', 'FK booking_id',
            'predicted_canceled', 'cancellation_prob',
            'not_cancelled_prob', 'features_used',
            'model_version', 'prediction_timestamp',
            'notes'
        ]
        for i, field in enumerate(fields5):
            ax.text(x5 + 0.2, y5 + height5 - 1.0 - i*0.35, field, 
                   ha='left', va='center', fontsize=8.5, family='monospace')
        
        # Arrows: bookings → predictions
        ax.annotate('', xy=(x5, y5 + height5), xytext=(x3 + width3/2, y3),
                   arrowprops=dict(arrowstyle='->', lw=2, color='purple'))
        ax.text((x3 + width3/2 + x5)/2, (y3 + y5 + height5)/2, 
               '1:N', ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='purple'))
        
        # Legend
        legend_y = 1.5
        ax.text(2, legend_y, 'Legend:', fontsize=11, fontweight='bold')
        ax.add_patch(FancyBboxPatch((1.5, legend_y - 0.4), 0.3, 0.2,
                                    facecolor='lightblue', edgecolor='black'))
        ax.text(2, legend_y - 0.3, 'Lookup Tables', ha='left', va='center', fontsize=9)
        
        ax.add_patch(FancyBboxPatch((1.5, legend_y - 0.9), 0.3, 0.2,
                                    facecolor='lightcoral', edgecolor='black'))
        ax.text(2, legend_y - 0.8, 'Main Tables', ha='left', va='center', fontsize=9)
        
        ax.add_patch(FancyBboxPatch((1.5, legend_y - 1.4), 0.3, 0.2,
                                    facecolor='lightgreen', edgecolor='black'))
        ax.text(2, legend_y - 1.3, 'Log/Audit Tables', ha='left', va='center', fontsize=9)
        
        ax.add_patch(FancyBboxPatch((1.5, legend_y - 1.9), 0.3, 0.2,
                                    facecolor='plum', edgecolor='black'))
        ax.text(2, legend_y - 1.8, 'ML/Analytics Tables', ha='left', va='center', fontsize=9)
        
        ax.text(10, legend_y - 0.8, 'PK = Primary Key  |  FK = Foreign Key', 
                ha='center', va='center', fontsize=10, style='italic')
        
        # Footer
        ax.text(10, 0.5, 'Generated with Python matplotlib', 
                ha='center', va='center', fontsize=9, style='italic')
        
        plt.tight_layout()
        # Save in the erd directory
        output_path = os.path.join('erd', 'ERD_Diagram.png')
        os.makedirs('erd', exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"ERD diagram saved as '{output_path}'")
        
        plt.close()
        
    if __name__ == "__main__":
        print("Generating ERD diagram...")
        create_erd()
        print("Done!")
        
except ImportError:
    print("matplotlib not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'matplotlib'])
    print("Please run the script again.")
except Exception as e:
    print(f"Error generating ERD: {e}")
    print("\nUsing alternative: Please use one of these tools to create the ERD:")
    print("1. dbdiagram.io - https://dbdiagram.io")
    print("2. draw.io - https://app.diagrams.net")
    print("3. MySQL Workbench")
