import axiosInstance from '@/helpers/axios-instance';
import { AuthData } from '@/lib/types';
import userState from '@/utils/user-state';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const useAuthData = (): AuthData => {
  const location = useLocation();
  const user = userState.getUser();

  const [data, setData] = useState<AuthData>({
    _id: user?._id || '',
    role: user?.role || '',
    token: '',
    loading: true,
  });

  useEffect(() => {
    setData((prev) => ({
      ...prev,
      _id: user?._id || '',
      role: user?.role || '',
      token: '',
      loading: true,
    }));
  }, [user?._id, user?.role]);

  useEffect(() => {
    if (!data._id) {
      setData((prev) => ({ ...prev, loading: false }));
      return;
    }

    async function fetchToken() {
      try {
        const res = await axiosInstance.get(`/api/auth/check/${data._id}`);
        setData((prev) => ({
          ...prev,
          token: res.data?.data,
          loading: false,
        }));
      } catch (error) {
        console.error('Error fetching token:', error);
        setData((prev) => ({
          ...prev,
          token: '',
          loading: false,
        }));
      }
    }
    fetchToken();
  }, [location.pathname, data._id]);

  return data;
};

export default useAuthData;
