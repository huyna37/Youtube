#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for the traffic simulator
"""

from browser_simulator import run_demo_traffic, print_traffic_stats, cleanup_profiles
import logging

def main():
    print("🚀 Testing Traffic Simulator for vpsx.me")
    print("="*50)
    
    # Run a quick demo with 2 visits
    try:
        print("Starting demo with 2 visits...")
        run_demo_traffic(2)
        print("\n✅ Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
        print_traffic_stats()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")
        
    finally:
        cleanup_profiles()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    main()
