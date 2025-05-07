import {create} from 'zustand';
import Cookies from 'js-cookie';
import {api} from '../lib/axios';

interface User {
    username : string;
    email: string;
}

interface AuthStore{
    user: User | null;
    isAuthenticated: boolean;
    login: (username: string, password: string) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    logout: () => void;
    fetchUser: () => Promise<void>;
}

interface RegisterData {
    username: string;
    email: string;
    password: string;
}

export const useAuthStore = create<AuthStore>((set) =>({
    user: null,
    isAuthenticated: !!Cookies.get("access_token"),

    login: async (username: string, password: string) => {
        const formdata = new URLSearchParams();
        formdata.append('username', username);
        formdata.append('password', password);

        const response = await api.post('/auth/login/access-token', formdata,{
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        const {access_token, refresh_token} = response.data;
        Cookies.set('access_token', access_token);
        Cookies.set('refresh_token', refresh_token);
        set({isAuthenticated:true});
    },

    register: async (data: RegisterData) => {
        await api.post('/auth/register', data);
    },
    logout :() =>{
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        set({isAuthenticated:false, user:null});
    },

    fetchUser: async () => {
        const response = await api.get('auth/users/me');
        set({ user: response.data });
      },
}));