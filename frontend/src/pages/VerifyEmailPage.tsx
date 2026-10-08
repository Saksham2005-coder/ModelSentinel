import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Shield, CheckCircle, XCircle } from 'lucide-react';
import { fetchApi } from '../services/api/client';

export const VerifyEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setErrorMsg('No verification token provided.');
      return;
    }

    const verifyToken = async () => {
      try {
        await fetchApi('/auth/verify-email', {
          method: 'POST',
          body: JSON.stringify({ token })
        });
        setStatus('success');
      } catch (err: unknown) {
        setStatus('error');
        if (err instanceof Error) {
          setErrorMsg(err.message || 'That verification link is invalid or has expired.');
        } else {
          setErrorMsg('That verification link is invalid or has expired.');
        }
      }
    };

    verifyToken();
  }, [token]);

  return (
    <div className="min-h-screen bg-background-base flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="flex justify-center mb-6">
          <Shield className="h-12 w-12 text-brand" />
        </div>
        <h2 className="mt-6 text-3xl font-bold tracking-tight text-text-primary">Email Verification</h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-background-primary/50 backdrop-blur-xl py-8 px-4 shadow-2xl shadow-black/50 sm:rounded-2xl sm:px-10 border border-border">
          
          {status === 'verifying' && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand mx-auto mb-4"></div>
              <p className="text-text-primary">Verifying your email address...</p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-text-primary mb-2">Email Verified Successfully</h3>
              <p className="text-text-secondary mb-6">Your account is now fully active.</p>
              <button
                onClick={() => navigate('/login')}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-black bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand focus:ring-offset-slate-900 transition-colors"
              >
                Continue to Sign In
              </button>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-text-primary mb-2">Verification Failed</h3>
              <p className="text-text-secondary mb-6">{errorMsg}</p>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/login')}
                  className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-black bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand focus:ring-offset-slate-900 transition-colors"
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
};
