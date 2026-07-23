import HomePage from '@/pages/home-page';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { afterEach, describe, expect, test, vi } from 'vitest';

const mockedUseNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockedUseNavigate,
  };
});

afterEach(() => {
  mockedUseNavigate.mockClear();
});

/**
 * To pass/clear test, backend must be running locally.
 */
describe('Integration Test: Home Route', () => {
  test('Home Route: Renders home page', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    expect(screen.getByText(/WanderLust/)).toBeInTheDocument();
    expect(
      screen.getByRole('button', {
        name: /Create post/i,
      })
    ).toBeInTheDocument();
    expect(screen.getByText(/Featured Posts/)).toBeInTheDocument();
    expect(screen.getAllByTestId('featurepostcardskeleton')).toHaveLength(5);
    expect(screen.getAllByTestId('latestpostcardskeleton')).toHaveLength(5);
    expect(screen.getByText(/All Posts/)).toBeInTheDocument();
    expect(screen.getAllByTestId('postcardskeleton')).toHaveLength(8);
  });

  test('Home Route: Verify navigation on create post button click', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    const createPost = screen.getByRole('button', {
      name: /Create post/i,
    });

    expect(mockedUseNavigate).toHaveBeenCalledTimes(0);

    await userEvent.click(createPost);

    expect(mockedUseNavigate).toHaveBeenCalledTimes(1);
  });

  test('Home Route: Verify filtered posts render on category button click', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    expect(screen.queryByTestId('featuredPostCard')).not.toBeInTheDocument();
    const featuredPostCard = await screen.findAllByTestId('featuredPostCard');
    expect(featuredPostCard).toHaveLength(5);
    const natureCategoryPill = screen.getByRole('button', {
      name: 'Nature',
    });
    expect(natureCategoryPill).toBeInTheDocument();
    await userEvent.click(natureCategoryPill);
    expect(await screen.findByText('Posts related to "Nature"')).toBeInTheDocument();
    expect(await screen.findAllByTestId('featuredPostCard')).toHaveLength(5);
  });

  test('Home Route: Verify navigation on post card click under Featured Posts section', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    const featuredPostCard = await screen.findAllByTestId('featuredPostCard');
    expect(featuredPostCard).toHaveLength(5);
    await userEvent.click(featuredPostCard[0]);
    expect(mockedUseNavigate).toHaveBeenCalledTimes(1);
  });

  test('Home Route: Verify render of post card under All Post section', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    expect(await screen.findAllByTestId('postcard')).toBeTruthy();
  });

  test('Home Route: Verify navigation on post card click under All Posts section', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    const allPostCard = await screen.findAllByTestId('postcard');
    const img = allPostCard[0].getElementsByTagName('img')[0];
    await userEvent.click(img);
    expect(mockedUseNavigate).toHaveBeenCalledTimes(1);
  });
});
