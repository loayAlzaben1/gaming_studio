#!/usr/bin/env python3
"""
Quick deployment script for cloud platforms
Makes your Gaming Studio available 24/7 online
"""
import os
import subprocess
import sys

def check_git_status():
    """Check if we're in a git repository and files are committed"""
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("📝 You have uncommitted changes:")
            print(result.stdout)
            
            commit = input("Do you want to commit and push these changes? (y/N): ").strip().lower()
            if commit == 'y':
                commit_msg = input("Enter commit message (or press Enter for default): ").strip()
                if not commit_msg:
                    commit_msg = "Update Gaming Studio for deployment"
                
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                
                push = input("Push to GitHub? (y/N): ").strip().lower()
                if push == 'y':
                    subprocess.run(['git', 'push'], check=True)
                    print("✅ Changes pushed to GitHub!")
            else:
                print("⚠️ Note: Uncommitted changes won't be deployed")
        else:
            print("✅ All changes are committed")
            
    except subprocess.CalledProcessError:
        print("❌ Not a git repository or git not installed")
        return False
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first")
        return False
    
    return True

def show_deployment_options():
    """Show available deployment platforms"""
    print("\n🚀 Deploy Your Gaming Studio to Stay Online 24/7")
    print("=" * 50)
    print("Choose a platform to deploy your website:")
    print()
    print("1. 🎯 Render.com (Recommended)")
    print("   - Free tier: 750 hours/month")
    print("   - Automatic SSL certificate")
    print("   - Easy GitHub integration")
    print("   - Custom domains available")
    print()
    print("2. 🟣 Heroku")
    print("   - Free tier discontinued, but reliable")
    print("   - Great for professional projects")
    print("   - Easy scaling")
    print()
    print("3. 🚂 Railway")
    print("   - $5 monthly free credit")
    print("   - Fast deployment")
    print("   - Great developer experience")
    print()
    print("4. 🐍 PythonAnywhere")
    print("   - Free tier with limitations")
    print("   - Python-focused hosting")
    print("   - Good for beginners")
    print()
    print("5. ℹ️  Show me how to deploy manually")
    print()

def get_deployment_instructions(platform):
    """Get specific deployment instructions for chosen platform"""
    instructions = {
        "1": {
            "name": "Render.com",
            "steps": [
                "1. Go to https://render.com and sign up with GitHub",
                "2. Click 'New' → 'Web Service'",
                "3. Connect your gaming_studio repository",
                "4. Set Build Command: python deploy.py",
                "5. Set Start Command: python -m waitress --host=0.0.0.0 --port=$PORT gaming_studio.wsgi:application",
                "6. Add Environment Variables:",
                "   - DJANGO_SECRET_KEY=your-secret-key-here",
                "   - DEBUG=False",
                "   - DEPLOY_ENV=render",
                "7. Click 'Create Web Service'",
                "8. Your site will be live at: https://your-app-name.onrender.com"
            ]
        },
        "2": {
            "name": "Heroku",
            "steps": [
                "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli",
                "2. Run: heroku login",
                "3. Run: heroku create your-app-name",
                "4. Run: heroku config:set DJANGO_SECRET_KEY=your-secret-key",
                "5. Run: heroku config:set DEBUG=False",
                "6. Run: git push heroku main",
                "7. Run: heroku run python manage.py migrate",
                "8. Your site will be live at: https://your-app-name.herokuapp.com"
            ]
        },
        "3": {
            "name": "Railway",
            "steps": [
                "1. Go to https://railway.app and sign up with GitHub",
                "2. Click 'New Project' → 'Deploy from GitHub repo'",
                "3. Select your gaming_studio repository",
                "4. Railway will auto-detect Django and deploy",
                "5. Add Environment Variables in Settings:",
                "   - DJANGO_SECRET_KEY=your-secret-key-here",
                "   - DEBUG=False",
                "6. Your site will be live at: https://your-app-name.up.railway.app"
            ]
        },
        "4": {
            "name": "PythonAnywhere",
            "steps": [
                "1. Go to https://pythonanywhere.com and create free account",
                "2. Open a Bash console",
                "3. Run: git clone https://github.com/your-username/gaming_studio.git",
                "4. Go to Web tab → Create new web app",
                "5. Choose Django → Python 3.10",
                "6. Set source code path to: /home/yourusername/gaming_studio",
                "7. Set WSGI file to: gaming_studio.wsgi",
                "8. Add environment variables in Files tab",
                "9. Your site will be live at: https://yourusername.pythonanywhere.com"
            ]
        }
    }
    
    return instructions.get(platform, None)

def main():
    print("🎮 Gaming Studio - Cloud Deployment Helper")
    print("=" * 50)
    print("Make your website available 24/7, even when your PC is off!")
    print()
    
    # Check git status
    if not check_git_status():
        print("\n❌ Please set up Git and push your code to GitHub first")
        return
    
    # Show deployment options
    show_deployment_options()
    
    while True:
        choice = input("Choose platform (1-5): ").strip()
        
        if choice in ["1", "2", "3", "4"]:
            instructions = get_deployment_instructions(choice)
            print(f"\n🚀 Deploying to {instructions['name']}")
            print("=" * 50)
            for step in instructions['steps']:
                print(step)
            print("\n✅ After deployment, your Gaming Studio will be online 24/7!")
            print("🔗 Share the URL with friends - they can access it anytime!")
            break
        elif choice == "5":
            print("\n📖 Manual Deployment Guide:")
            print("Check the DEPLOYMENT_GUIDE.md file for detailed instructions")
            os.system("notepad DEPLOYMENT_GUIDE.md" if os.name == "nt" else "cat DEPLOYMENT_GUIDE.md")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
