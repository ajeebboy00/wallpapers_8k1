import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

typedef DownloadProgressCallback = void Function(int received, int total, double percent);

abstract class IDownloadService {
  Future<String> downloadFile({
    required String url,
    required String filename,
    DownloadProgressCallback? onProgress,
  });
}

class DownloadService implements IDownloadService {
  final Dio _dio;

  DownloadService([Dio? dio]) : _dio = dio ?? Dio();

  @override
  Future<String> downloadFile({
    required String url,
    required String filename,
    DownloadProgressCallback? onProgress,
  }) async {
    final Directory cacheDir = await getTemporaryDirectory();
    final String savePath = '${cacheDir.path}/$filename';

    // Check if already cached
    final File existingFile = File(savePath);
    if (await existingFile.exists() && (await existingFile.length()) > 0) {
      if (onProgress != null) {
        final len = await existingFile.length();
        onProgress(len, len, 1.0);
      }
      return savePath;
    }

    await _dio.download(
      url,
      savePath,
      onReceiveProgress: (received, total) {
        if (total > 0 && onProgress != null) {
          final percent = (received / total).clamp(0.0, 1.0);
          onProgress(received, total, percent);
        }
      },
      options: Options(
        responseType: ResponseType.bytes,
        followRedirects: true,
      ),
    );

    return savePath;
  }
}
