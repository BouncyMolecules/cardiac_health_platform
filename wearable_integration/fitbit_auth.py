import streamlit as st
import requests
from requests_oauthlib import OAuth2Session
import json
import time
from urllib.parse import urlparse, parse_qs
from config.fitbit_config import fitbit_config

class FitbitAuth:
    def __init__(self):
        self.client_id = fitbit_config.CLIENT_ID
        self.client_secret = fitbit_config.CLIENT_SECRET
        self.redirect_uri = fitbit_config.REDIRECT_URI
        self.scope = " ".join(fitbit_config.SCOPES)
        
    def get_authorization_url(self):
        """Get the Fitbit authorization URL"""
        oauth = OAuth2Session(
            self.client_id, 
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        authorization_url, state = oauth.authorization_url(
            fitbit_config.AUTHORIZE_URL,
            access_type="offline",
            prompt="login"
        )
        st.session_state['oauth_state'] = state
        return authorization_url
    
    def fetch_token(self, authorization_response):
        """Exchange authorization code for access token"""
        oauth = OAuth2Session(
            self.client_id,
            state=st.session_state.get('oauth_state'),
            redirect_uri=self.redirect_uri
        )
        
        try:
            token = oauth.fetch_token(
                fitbit_config.TOKEN_URL,
                authorization_response=authorization_response,
                client_secret=self.client_secret,
                include_client_id=True
            )
            
            # Store token in session state
            st.session_state['fitbit_token'] = token
            st.session_state['fitbit_connected'] = True
            st.session_state['token_expires_at'] = time.time() + token.get('expires_in', 28800)
            
            return token
        except Exception as e:
            st.error(f"Error fetching token: {e}")
            return None
    
    def refresh_token(self):
        """Refresh access token using refresh token"""
        if 'fitbit_token' not in st.session_state:
            return None
            
        token = st.session_state['fitbit_token']
        refresh_token = token.get('refresh_token')
        
        if not refresh_token:
            return None
            
        try:
            response = requests.post(
                fitbit_config.TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            if response.status_code == 200:
                new_token = response.json()
                st.session_state['fitbit_token'] = new_token
                st.session_state['token_expires_at'] = time.time() + new_token.get('expires_in', 28800)
                return new_token
            else:
                st.error(f"Token refresh failed: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error refreshing token: {e}")
            return None
    
    def get_valid_token(self):
        """Get valid access token, refreshing if necessary"""
        if 'fitbit_token' not in st.session_state:
            return None
            
        token = st.session_state['fitbit_token']
        expires_at = st.session_state.get('token_expires_at', 0)
        
        # Refresh token if it expires in less than 5 minutes
        if time.time() > (expires_at - 300):
            return self.refresh_token() or token
        else:
            return token
    
    def is_authenticated(self):
        """Check if user is authenticated with valid token"""
        if not st.session_state.get('fitbit_connected'):
            return False
            
        token = self.get_valid_token()
        return token is not None
    
    def get_headers(self):
        """Get headers for API requests"""
        token = self.get_valid_token()
        if not token:
            return None
            
        return {
            'Authorization': f"Bearer {token['access_token']}",
            'Accept': 'application/json',
            'Accept-Language': 'en_US'
        }
    
    def revoke_access(self):
        """Revoke Fitbit access"""
        if 'fitbit_token' in st.session_state:
            del st.session_state['fitbit_token']
        if 'fitbit_connected' in st.session_state:
            del st.session_state['fitbit_connected']
        if 'token_expires_at' in st.session_state:
            del st.session_state['token_expires_at']