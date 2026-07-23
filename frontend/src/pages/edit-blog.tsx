import FormBlog from '@/components/form-blog';
import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import Post from '@/types/post-type';
import axios from 'axios';
import useAuthData from '@/hooks/useAuthData';

const EditBlog = () => {
  const { state } = useLocation();
  const [post, setPost] = useState<Post>(state?.post);
  const initialVal = post === undefined;
  const [loading, setIsLoading] = useState(initialVal);
  const { postId } = useParams();

  const userData = useAuthData();
  const navigate = useNavigate();

  useEffect(() => {
    const getPostById = async () => {
      try {
        await axios.get(import.meta.env.VITE_API_PATH + `/api/posts/${postId}`).then((response) => {
          setIsLoading(false);
          setPost(response.data);
        });
      } catch (error) {
        console.log(error);
      }
    };
    if (post === undefined || post !== state?.post) {
      getPostById();
    }
  }, [post, postId, state?.post]);

  useEffect(() => {
    if (
      !loading &&
      userData?.role === 'USER' &&
      post?.authorId &&
      String(post.authorId) !== String(userData?._id)
    ) {
      navigate(-1);
    }
  }, [loading, userData?.role, userData?._id, post?.authorId, navigate]);

  if (!loading) {
    return (
      <>
        <FormBlog postId={postId} type="edit" post={post} />
      </>
    );
  } else return <h1>Loading...</h1>;
};

export default EditBlog;
